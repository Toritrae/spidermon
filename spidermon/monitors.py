from .managers import RulesManager
from .serialization import JSONSerializable
from .debug import MonitorResultsReport, MonitorReport
from . import settings


class MonitorResult(JSONSerializable):
    def __init__(self, monitor, checks=None, stats=None):
        self.monitor = monitor
        self.checks = checks or []
        self.stats = stats or {}

    def to_json(self):
        data = {
            'monitor': self.monitor.name,
            'checks': self.checks,
            'stats': self.stats,
            'summary': {
                'rules': {
                    'total': len(self.monitor.rules_manager.definitions),
                },
            }
        }
        data['summary']['rules'].update(self._get_check_counts())
        return data

    @property
    def passed_checks(self):
        return self._get_checks(settings.CHECK_STATE_PASSED)

    @property
    def failed_checks(self):
        return self._get_checks(settings.CHECK_STATE_FAILED)

    @property
    def error_checks(self):
        return self._get_checks(settings.CHECK_STATE_ERROR)

    @property
    def n_passed_checks(self):
        return len(self.passed_checks)

    @property
    def n_failed_checks(self):
        return len(self.failed_checks)

    @property
    def n_error_checks(self):
        return len(self.error_checks)

    def _get_checks(self, state):
        return [c for c in self.checks if c.state == state]

    def _get_check_count(self, state):
        return len(self._get_checks(state))

    def _get_check_counts(self):
        return dict([(state, self._get_check_count(state)) for state in settings.CHECK_STATES])

    def debug(self):
        report = MonitorResultsReport(self)
        return report.render()


class Monitor(object):
    def __init__(self, name=None, rules=None):
        self.name = name or '?'
        self.rules_manager = RulesManager(rules)
        self.add_rule = self.rules_manager.add_rule

    def run(self, stats):
        result = MonitorResult(self)
        result.checks = self.rules_manager.check_rules(stats)
        result.stats = stats
        return result

    def debug(self):
        report = MonitorReport(self)
        return report.render()
