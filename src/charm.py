#!/usr/bin/env python3

# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

"""DNS Integrator Charm."""

import logging
import typing
import uuid

import ops
from charms.bind.v0 import dns_record

logger = logging.getLogger(__name__)

VALID_LOG_LEVELS = ["info", "debug", "warning", "error", "critical"]


class DnsIntegratorOperatorCharm(ops.CharmBase):
    """Charm the service."""

    def __init__(self, *args: typing.Any):
        """Construct.

        Args:
            args: Arguments passed to the CharmBase parent constructor.
        """
        super().__init__(*args)
        self.dns_record = dns_record.DNSRecordRequires(self)
        self.framework.observe(self.on.config_changed, self._on_config_changed)

    def _on_config_changed(self, _: ops.ConfigChangedEvent) -> None:
        """Handle changes in configuration."""
        self.unit.status = ops.MaintenanceStatus("Configuring charm")
        self._update_relations()
        self.unit.status = ops.ActiveStatus()

    def _update_relations(self) -> None:
        """Update all DNS data for the existing relations."""
        if not self.model.unit.is_leader():
            return
        for relation in self.model.relations[self.dns_record.relation_name]:
            self.dns_record.update_relation_data(relation, self._get_dns_record_requirer_data())

    def _get_dns_record_requirer_data(self) -> dns_record.DNSRecordRequirerData:
        """Get DNS record requirer data."""
        entry = dns_record.RequirerEntry(
            domain=self.config["domain"],
            host_label=self.config["host_label"],
            ttl=self.config.get("ttl", 600),
            record_class=self.config.get("record_class", "IN"),
            record_type=self.config.get("record_type", "A"),
            record_data=self.config["record_data"],
            uuid=uuid.uuid4(),
        )
        logger.debug("DNS record request: %s", entry)
        return dns_record.DNSRecordRequirerData(
            dns_entries=[entry],
        )


if __name__ == "__main__":  # pragma: nocover
    ops.main(DnsIntegratorOperatorCharm)  # type: ignore
