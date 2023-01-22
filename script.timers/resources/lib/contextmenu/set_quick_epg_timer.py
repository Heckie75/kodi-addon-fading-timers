from resources.lib.contextmenu.abstract_set_timer import (CONFIRM_YES,
                                                          AbstractSetTimer)
from resources.lib.timer.concurrency import get_next_higher_prio
from resources.lib.timer.timer import Timer


class SetQuickEpgTimer(AbstractSetTimer):

    def perform_ahead(self, timer: Timer) -> bool:

        timers = self.storage.load_timers_from_storage()

        found = -1
        for i, t in enumerate(timers):
            if (found == -1
                    and timer.days == t.days
                    and timer.start == t.start
                    and timer.path == t.path):

                found = i

        if found != -1:
            timer.id = timers[found].id

        return True

    def ask_duration(self, label: str, path: str, is_epg: bool, timer: Timer) -> str:

        return timer.duration

    def ask_repeat_resume(self, timer: Timer) -> 'tuple[bool, bool]':

        return False, True

    def handle_overlapping_timers(self, timer: Timer, overlapping_timers: 'list[Timer]') -> int:

        timer.priority = get_next_higher_prio(overlapping_timers)
        return CONFIRM_YES

    def confirm(self, timer: Timer) -> int:

        return CONFIRM_YES
