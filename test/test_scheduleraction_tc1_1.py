import unittest
from datetime import timedelta

from resources.lib.player.mediatype import AUDIO, VIDEO, PICTURE
from resources.lib.test.mockplayer import MockPlayer
from resources.lib.timer.scheduleraction import SchedulerAction
from resources.lib.timer.timer import (END_TYPE_DURATION, FADE_IN_FROM_MIN,
                                       FADE_OFF, FADE_OUT_FROM_CURRENT,
                                       MEDIA_ACTION_START_STOP,
                                       SYSTEM_ACTION_NONE, Period, Timer)


class TestSchedulerActions_1_1(unittest.TestCase):

    _t0 = 0
    _t1 = 60
    _t2 = 120
    _t3 = 180
    _t4 = 240
    _t5 = 300
    _t6 = 360
    _t7 = 420
    _t8 = 480
    _t9 = 520
    _t10 = 600

    def test_tc_1_1(self):
        """
        TC 1.1. Single video timer w/ resume but w/o former media

        Timer 1           |-----------------R

        t       |---------|-------T1--------|---------------->
                t0        t1       t2       t3       t4
        Player            play              stop

        Fader   100       T1(100)-----------T1(50)
        """

        # ------------ setup player ------------d
        player = MockPlayer()
        schedulderaction = SchedulerAction(player)
        player.setVolume(100)

        # ------------ setup timers ------------
        # Timer 1 (T1)
        timer1 = Timer(1)
        timer1.label = "Timer 1"
        timer1.end_type = END_TYPE_DURATION
        timer1.duration_timedelta = timedelta(minutes=self._t3 - self._t1)
        timer1.media_action = MEDIA_ACTION_START_STOP
        timer1.path = "Media T1"
        timer1.media_type = VIDEO
        timer1.repeat = False
        timer1.resume = True
        timer1.fade = FADE_OUT_FROM_CURRENT
        timer1.vol_min = 50
        timer1.vol_max = 100
        timer1.system_action = SYSTEM_ACTION_NONE
        timer1.active = False
        timer1.notify = False
        timer1.periods = [
            Period(timedelta(minutes=self._t1), timedelta(minutes=self._t3))]

        timers = [timer1]

        # ------------ t0 ------------
        schedulderaction.calculate(
            timers, None, timedelta(minutes=self._t0))

        self.assertEqual(timers[0].active, False)
        self.assertEqual(len(schedulderaction._beginningTimers), 0)
        self.assertEqual(len(schedulderaction._runningTimers), 0)
        self.assertEqual(len(schedulderaction._endingTimers), 0)
        self.assertEqual(schedulderaction._fader, None)
        self.assertEqual(schedulderaction._timerToPlayAV, None)
        self.assertEqual(schedulderaction._timerToStopAV, None)
        self.assertEqual(schedulderaction._timerWithSystemAction, None)

        schedulderaction.perform(timedelta(minutes=self._t0))

        apwpl = player.getActivePlayersWithPlaylist()
        self.assertEqual(len(apwpl), 0)
        self.assertEqual(player._getResumeStatus(VIDEO), None)
        self.assertEqual(player.getVolume(), 100)

        schedulderaction.reset()

        # ------------ t1 ------------
        schedulderaction.calculate(
            timers, None, timedelta(minutes=self._t1))

        self.assertEqual(timers[0].active, True)
        self.assertEqual(len(schedulderaction._beginningTimers), 1)
        self.assertEqual(len(schedulderaction._runningTimers), 0)
        self.assertEqual(len(schedulderaction._endingTimers), 0)
        self.assertEqual(schedulderaction._fader.timer.label, timers[0].label)
        self.assertEqual(
            schedulderaction._timerToPlayAV.timer.id, timers[0].id)
        self.assertEqual(schedulderaction._timerToStopAV, None)
        self.assertEqual(schedulderaction._timerWithSystemAction, None)

        schedulderaction.perform(timedelta(minutes=self._t1))

        apwpl = player.getActivePlayersWithPlaylist()
        self.assertEqual(VIDEO in apwpl, True)
        self.assertEqual(apwpl[VIDEO].playlist[0]
                         ["file"], timers[0].path)
        self.assertEqual(player.getVolume(), 100)
        self.assertNotEqual(player._getResumeStatus(VIDEO), None)
        self.assertEqual(player._getResumeStatus(
            VIDEO).timer.id, timers[0].id)
        self.assertEqual(player._getResumeStatus(VIDEO).state, None)

        schedulderaction.reset()

        # ------------ t2 ------------
        schedulderaction.calculate(
            timers, None, timedelta(minutes=self._t2))

        self.assertEqual(timers[0].active, True)
        self.assertEqual(len(schedulderaction._beginningTimers), 0)
        self.assertEqual(len(schedulderaction._runningTimers), 1)
        self.assertEqual(len(schedulderaction._endingTimers), 0)
        self.assertEqual(schedulderaction._fader.timer.label, timers[0].label)
        self.assertEqual(schedulderaction._timerToPlayAV, None)
        self.assertEqual(schedulderaction._timerToStopAV, None)
        self.assertEqual(schedulderaction._timerWithSystemAction, None)

        schedulderaction.perform(timedelta(minutes=self._t2))

        apwpl = player.getActivePlayersWithPlaylist()
        self.assertEqual(VIDEO in apwpl, True)
        self.assertEqual(apwpl[VIDEO].playlist[0]
                         ["file"], timers[0].path)
        self.assertNotEqual(player._getResumeStatus(VIDEO), None)
        self.assertEqual(player._getResumeStatus(
            VIDEO).timer.id, timers[0].id)
        self.assertEqual(player._getResumeStatus(VIDEO).state, None)
        self.assertEqual(player.getVolume(), 75)

        schedulderaction.reset()

        # ------------ t3 ------------
        schedulderaction.calculate(
            timers, None, timedelta(minutes=self._t3))

        self.assertEqual(timers[0].active, False)
        self.assertEqual(len(schedulderaction._beginningTimers), 0)
        self.assertEqual(len(schedulderaction._runningTimers), 0)
        self.assertEqual(len(schedulderaction._endingTimers), 1)
        self.assertEqual(schedulderaction._fader, None)
        self.assertEqual(schedulderaction._timerToPlayAV, None)
        self.assertEqual(
            schedulderaction._timerToStopAV.timer.id, timers[0].id)
        self.assertEqual(schedulderaction._timerWithSystemAction, None)

        schedulderaction.perform(timedelta(minutes=self._t3))

        apwpl = player.getActivePlayersWithPlaylist()
        self.assertEqual(len(apwpl), 0)
        self.assertEqual(player.getVolume(), 100)
        self.assertEqual(player._getResumeStatus(AUDIO), None)
        self.assertEqual(player._getResumeStatus(VIDEO), None)
        self.assertEqual(player._getResumeStatus(PICTURE), None)

        schedulderaction.reset()

        # ------------ t4 ------------
        schedulderaction.calculate(
            timers, None, timedelta(minutes=self._t4))

        self.assertEqual(timers[0].active, False)
        self.assertEqual(
            len(schedulderaction._beginningTimers), 0)
        self.assertEqual(len(schedulderaction._runningTimers), 0)
        self.assertEqual(len(schedulderaction._endingTimers), 0)
        self.assertEqual(schedulderaction._fader, None)
        self.assertEqual(schedulderaction._timerToPlayAV, None)
        self.assertEqual(schedulderaction._timerToStopAV, None)
        self.assertEqual(
            schedulderaction._timerWithSystemAction, None)

        schedulderaction.perform(timedelta(minutes=self._t4))

        apwpl = player.getActivePlayersWithPlaylist()
        self.assertEqual(len(apwpl), 0)
        self.assertEqual(player._getResumeStatus(VIDEO), None)
        self.assertEqual(player.getVolume(), 100)

        schedulderaction.reset()
