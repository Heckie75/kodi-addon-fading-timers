import unittest
from datetime import timedelta

from resources.lib.player.mediatype import AUDIO, PICTURE, VIDEO
from resources.lib.test.mockplayer import MockPlayer
from resources.lib.timer.scheduleraction import SchedulerAction
from resources.lib.timer.timer import (END_TYPE_DURATION, FADE_IN_FROM_MIN,
                                       FADE_OFF, FADE_OUT_FROM_CURRENT,
                                       FADE_OUT_FROM_MAX, MEDIA_ACTION_START_AT_END,
                                       MEDIA_ACTION_START_STOP, MEDIA_ACTION_STOP_START,
                                       SYSTEM_ACTION_NONE,
                                       SYSTEM_ACTION_SHUTDOWN_KODI, Period,
                                       Timer)


class TestSchedulerActions_6(unittest.TestCase):

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

    def test_tc_6_1_1(self):
        """
        Media 1 |---------|                            |---------------->
        Timer 1           |----------S                                      (Systemaction)
        Timer 2                      |-----------------R

        t       |----M1---|----T1----|-----------------|----------------->
                t0        t1   t2    t3      t4        t5      t6
        Player            play       Shutdown
        """

        # ------------ setup player ------------
        player = MockPlayer()
        playlist = player._buildPlaylist(["Media M1"], VIDEO)
        player.play(playlist)
        player.setDefaultVolume(100)
        player.setVolume(80)

        schedulderaction = SchedulerAction(player)
        schedulderaction.__is_unit_test__ = True

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
        timer1.system_action = SYSTEM_ACTION_SHUTDOWN_KODI
        timer1.active = False
        timer1.notify = False
        timer1.periods = [
            Period(timedelta(minutes=self._t1), timedelta(minutes=self._t3))]

        # Timer 2 (T2)
        timer2 = Timer(2)
        timer2.label = "Timer 2"
        timer2.end_type = END_TYPE_DURATION
        timer2.duration_timedelta = timedelta(minutes=self._t5 - self._t3)
        timer2.media_action = MEDIA_ACTION_START_STOP
        timer2.path = "Media T2"
        timer2.media_type = VIDEO
        timer2.repeat = False
        timer2.resume = True
        timer2.fade = FADE_OFF
        timer2.vol_min = 0
        timer2.vol_max = 100
        timer2.system_action = SYSTEM_ACTION_NONE
        timer2.active = False
        timer2.notify = False
        timer2.periods = [
            Period(timedelta(minutes=self._t3), timedelta(minutes=self._t5))]

        timers = [timer1, timer2]

        # ------------ t0 ------------
        schedulderaction.calculate(
            timers, timedelta(minutes=self._t0))

        self.assertEqual(timers[0].active, False)
        self.assertEqual(timers[1].active, False)
        self.assertEqual(len(schedulderaction._getBeginningTimers()), 0)
        self.assertEqual(len(schedulderaction._getRunningTimers()), 0)
        self.assertEqual(len(schedulderaction._getEndingTimers()), 0)
        self.assertEqual(schedulderaction._getFader(), None)
        self.assertEqual(schedulderaction._getTimerToPlayAV(), None)
        self.assertEqual(schedulderaction._getTimerToStopAV(), None)
        self.assertEqual(schedulderaction._getTimerWithSystemAction(), None)
        

        schedulderaction.perform(timedelta(minutes=self._t0))

        apwpl = player.getActivePlayersWithPlaylist()
        self.assertEqual(VIDEO in apwpl, True)
        self.assertEqual(apwpl[VIDEO].playlist[0]["file"], "Media M1")
        self.assertEqual(player.getVolume(), 80)
        self.assertEqual(player._getResumeStatus(VIDEO), None)

        schedulderaction.reset()

        # ------------ t1 ------------
        schedulderaction.calculate(
            timers, timedelta(minutes=self._t1))

        self.assertEqual(timers[0].active, True)
        self.assertEqual(timers[1].active, False)
        self.assertEqual(len(schedulderaction._getBeginningTimers()), 1)
        self.assertEqual(len(schedulderaction._getRunningTimers()), 0)
        self.assertEqual(len(schedulderaction._getEndingTimers()), 0)
        self.assertEqual(schedulderaction._getFader(
        ).getTimer().id, timers[0].id)
        self.assertEqual(schedulderaction._getTimerToPlayAV(
        ).getTimer().id, timers[0].id)
        self.assertEqual(schedulderaction._getTimerToStopAV(), None)
        self.assertEqual(schedulderaction._getTimerWithSystemAction(), None)
        

        schedulderaction.perform(timedelta(minutes=self._t1))

        apwpl = player.getActivePlayersWithPlaylist()
        self.assertEqual(VIDEO in apwpl, True)
        self.assertEqual(apwpl[VIDEO].playlist[0]
                         ["file"], timers[0].path)
        self.assertEqual(player.getVolume(), 80)
        self.assertNotEqual(player._getResumeStatus(VIDEO), None)
        self.assertEqual(player._getResumeStatus(
            VIDEO)._timer.id, timers[0].id)
        self.assertEqual(player._getResumeStatus(
            VIDEO)._state.playlist[0]["file"], "Media M1")

        schedulderaction.reset()

        # ------------ t2 ------------
        schedulderaction.calculate(
            timers, timedelta(minutes=self._t2))

        self.assertEqual(timers[0].active, True)
        self.assertEqual(timers[1].active, False)
        self.assertEqual(len(schedulderaction._getBeginningTimers()), 0)
        self.assertEqual(len(schedulderaction._getRunningTimers()), 1)
        self.assertEqual(len(schedulderaction._getEndingTimers()), 0)
        self.assertEqual(schedulderaction._getFader(
        ).getTimer().id, timers[0].id)
        self.assertEqual(schedulderaction._getTimerToPlayAV(), None)
        self.assertEqual(schedulderaction._getTimerToStopAV(), None)
        self.assertEqual(schedulderaction._getTimerWithSystemAction(), None)
        

        schedulderaction.perform(timedelta(minutes=self._t2))

        apwpl = player.getActivePlayersWithPlaylist()
        self.assertEqual(VIDEO in apwpl, True)
        self.assertEqual(apwpl[VIDEO].playlist[0]
                         ["file"], timers[0].path)
        self.assertEqual(player.getVolume(), 65)
        self.assertNotEqual(player._getResumeStatus(VIDEO), None)
        self.assertEqual(player._getResumeStatus(
            VIDEO)._timer.id, timers[0].id)
        self.assertEqual(player._getResumeStatus(
            VIDEO)._state.playlist[0]["file"], "Media M1")

        schedulderaction.reset()

        # ------------ t3 ------------
        schedulderaction.calculate(
            timers, timedelta(minutes=self._t3))

        self.assertEqual(timers[0].active, False)
        self.assertEqual(timers[1].active, True)
        self.assertEqual(len(schedulderaction._getBeginningTimers()), 1)
        self.assertEqual(len(schedulderaction._getRunningTimers()), 0)
        self.assertEqual(len(schedulderaction._getEndingTimers()), 1)
        self.assertEqual(schedulderaction._getFader(), None)
        self.assertEqual(schedulderaction._getTimerToPlayAV(), None)
        self.assertEqual(schedulderaction._getTimerToStopAV(
        ).getTimer().id, timers[0].id)
        self.assertEqual(schedulderaction._getTimerToStopSlideshow(
        ).getTimer().id, timers[0].id)
        self.assertEqual(schedulderaction._getTimerWithSystemAction(
        ).getTimer().id, timers[0].id)
        

        schedulderaction.perform(timedelta(minutes=self._t3))

        apwpl = player.getActivePlayersWithPlaylist()
        self.assertEqual(len(apwpl), 0)
        self.assertEqual(player.getVolume(), 100)
        self.assertEqual(player._getResumeStatus(AUDIO), None)
        self.assertEqual(player._getResumeStatus(VIDEO), None)
        self.assertEqual(player._getResumeStatus(PICTURE), None)

        schedulderaction.reset()

    def test_tc_6_1_2(self):
        """
        Media 1 |---------|
        Timer 1           |------------------>
        Timer 2                      |-----------------R

        t       |----M1---|----M1----|---T2---|---T1---|-------T1-------->
                t0        t1    t2   t3  t4  t5   t6   t7   t8
        Player            n/a        play     Play     n/a
        """

        # ------------ setup player ------------
        player = MockPlayer()
        playlist = player._buildPlaylist(["Media M1"], VIDEO)
        player.setVolume(80)
        player.play(playlist)

        schedulderaction = SchedulerAction(player)

        # ------------ setup timers ------------
        # Timer 1 (T1)
        timer1 = Timer(1)
        timer1.label = "Timer 1"
        timer1.end_type = END_TYPE_DURATION
        timer1.duration_timedelta = timedelta(minutes=self._t5 - self._t1)
        timer1.media_action = MEDIA_ACTION_START_AT_END
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
            Period(timedelta(minutes=self._t1), timedelta(minutes=self._t5))]

        # Timer 2 (T2)
        timer2 = Timer(2)
        timer2.label = "Timer 2"
        timer2.end_type = END_TYPE_DURATION
        timer2.duration_timedelta = timedelta(minutes=self._t7 - self._t3)
        timer2.media_action = MEDIA_ACTION_START_STOP
        timer2.path = "Media T2"
        timer2.media_type = VIDEO
        timer2.repeat = False
        timer2.resume = True
        timer2.fade = FADE_OFF
        timer2.vol_min = 0
        timer2.vol_max = 100
        timer2.system_action = SYSTEM_ACTION_NONE
        timer2.active = False
        timer2.notify = False
        timer2.periods = [
            Period(timedelta(minutes=self._t3), timedelta(minutes=self._t7))]

        timers = [timer1, timer2]

        # ------------ t0 ------------
        schedulderaction.calculate(
            timers, timedelta(minutes=self._t0))

        self.assertEqual(timers[0].active, False)
        self.assertEqual(timers[1].active, False)
        self.assertEqual(len(schedulderaction._getBeginningTimers()), 0)
        self.assertEqual(len(schedulderaction._getRunningTimers()), 0)
        self.assertEqual(len(schedulderaction._getEndingTimers()), 0)
        self.assertEqual(schedulderaction._getFader(), None)
        self.assertEqual(schedulderaction._getTimerToPlayAV(), None)
        self.assertEqual(schedulderaction._getTimerToStopAV(), None)
        self.assertEqual(schedulderaction._getTimerWithSystemAction(), None)
        

        schedulderaction.perform(timedelta(minutes=self._t0))

        apwpl = player.getActivePlayersWithPlaylist()
        self.assertEqual(VIDEO in apwpl, True)
        self.assertEqual(apwpl[VIDEO].playlist[0]["file"], "Media M1")
        self.assertEqual(player.getVolume(), 80)
        self.assertEqual(player._getResumeStatus(VIDEO), None)

        schedulderaction.reset()

        # ------------ t1 ------------
        schedulderaction.calculate(
            timers, timedelta(minutes=self._t1))

        self.assertEqual(timers[0].active, True)
        self.assertEqual(timers[1].active, False)
        self.assertEqual(len(schedulderaction._getBeginningTimers()), 1)
        self.assertEqual(len(schedulderaction._getRunningTimers()), 0)
        self.assertEqual(len(schedulderaction._getEndingTimers()), 0)
        self.assertEqual(schedulderaction._getFader(
        ).getTimer().id, timers[0].id)
        self.assertEqual(schedulderaction._getTimerToPlayAV(), None)
        self.assertEqual(schedulderaction._getTimerToStopAV(), None)
        self.assertEqual(schedulderaction._getTimerWithSystemAction(), None)
        

        schedulderaction.perform(timedelta(minutes=self._t1))

        apwpl = player.getActivePlayersWithPlaylist()
        self.assertEqual(VIDEO in apwpl, True)
        self.assertEqual(apwpl[VIDEO].playlist[0]["file"], "Media M1")
        self.assertEqual(player.getVolume(), 80)
        self.assertEqual(player._getResumeStatus(VIDEO), None)

        schedulderaction.reset()

        # ------------ t2 ------------
        schedulderaction.calculate(
            timers, timedelta(minutes=self._t2))

        self.assertEqual(timers[0].active, True)
        self.assertEqual(timers[1].active, False)
        self.assertEqual(len(schedulderaction._getBeginningTimers()), 0)
        self.assertEqual(len(schedulderaction._getRunningTimers()), 0)
        self.assertEqual(len(schedulderaction._getEndingTimers()), 0)
        self.assertEqual(schedulderaction._getFader(
        ).getTimer().id, timers[0].id)
        self.assertEqual(schedulderaction._getTimerToPlayAV(), None)
        self.assertEqual(schedulderaction._getTimerToStopAV(), None)
        self.assertEqual(schedulderaction._getTimerWithSystemAction(), None)
        

        schedulderaction.perform(timedelta(minutes=self._t2))

        apwpl = player.getActivePlayersWithPlaylist()
        self.assertEqual(VIDEO in apwpl, True)
        self.assertEqual(apwpl[VIDEO].playlist[0]["file"], "Media M1")
        self.assertEqual(player.getVolume(), 72)
        self.assertEqual(player._getResumeStatus(VIDEO), None)

        schedulderaction.reset()

        # ------------ t3 ------------
        schedulderaction.calculate(
            timers, timedelta(minutes=self._t3))

        self.assertEqual(timers[0].active, True)
        self.assertEqual(timers[1].active, True)
        self.assertEqual(len(schedulderaction._getBeginningTimers()), 1)
        self.assertEqual(len(schedulderaction._getRunningTimers()), 0)
        self.assertEqual(len(schedulderaction._getEndingTimers()), 0)
        self.assertEqual(schedulderaction._getFader(
        ).getTimer().id, timers[0].id)
        self.assertEqual(schedulderaction._getTimerToPlayAV(
        ).getTimer().id, timers[1].id)
        self.assertEqual(schedulderaction._getTimerToStopAV(), None)
        self.assertEqual(schedulderaction._getTimerWithSystemAction(), None)
        

        schedulderaction.perform(timedelta(minutes=self._t3))

        apwpl = player.getActivePlayersWithPlaylist()
        self.assertEqual(VIDEO in apwpl, True)
        self.assertEqual(apwpl[VIDEO].playlist[0]
                         ["file"], timers[1].path)
        self.assertEqual(player.getVolume(), 65)
        self.assertNotEqual(player._getResumeStatus(VIDEO), None)
        self.assertEqual(player._getResumeStatus(
            VIDEO)._timer.id, timers[1].id)
        self.assertEqual(player._getResumeStatus(
            VIDEO)._state.playlist[0]["file"], "Media M1")

        schedulderaction.reset()

        # ------------ t4 ------------
        schedulderaction.calculate(
            timers, timedelta(minutes=self._t4))

        self.assertEqual(timers[0].active, True)
        self.assertEqual(timers[1].active, True)
        self.assertEqual(len(schedulderaction._getBeginningTimers()), 0)
        self.assertEqual(len(schedulderaction._getRunningTimers()), 1)
        self.assertEqual(len(schedulderaction._getEndingTimers()), 0)
        self.assertEqual(schedulderaction._getFader(
        ).getTimer().id, timers[0].id)
        self.assertEqual(schedulderaction._getTimerToPlayAV(), None)
        self.assertEqual(schedulderaction._getTimerToStopAV(), None)
        self.assertEqual(schedulderaction._getTimerWithSystemAction(), None)
        

        schedulderaction.perform(timedelta(minutes=self._t4))

        apwpl = player.getActivePlayersWithPlaylist()
        self.assertEqual(VIDEO in apwpl, True)
        self.assertEqual(apwpl[VIDEO].playlist[0]
                         ["file"], timers[1].path)
        self.assertEqual(player.getVolume(), 58)
        self.assertNotEqual(player._getResumeStatus(VIDEO), None)
        self.assertEqual(player._getResumeStatus(
            VIDEO)._timer.id, timers[1].id)
        self.assertEqual(player._getResumeStatus(
            VIDEO)._state.playlist[0]["file"], "Media M1")

        schedulderaction.reset()

        # ------------ t5 ------------
        schedulderaction.calculate(
            timers, timedelta(minutes=self._t5))

        self.assertEqual(timers[0].active, False)
        self.assertEqual(timers[1].active, True)
        self.assertEqual(len(schedulderaction._getBeginningTimers()), 0)
        self.assertEqual(len(schedulderaction._getRunningTimers()), 1)
        self.assertEqual(len(schedulderaction._getEndingTimers()), 1)
        self.assertEqual(schedulderaction._getFader(), None)
        self.assertEqual(schedulderaction._getTimerToPlayAV(
        ).getTimer().id, timers[0].id)
        self.assertEqual(schedulderaction._getTimerToStopAV(), None)
        self.assertEqual(schedulderaction._getTimerWithSystemAction(), None)
        

        schedulderaction.perform(timedelta(minutes=self._t5))

        apwpl = player.getActivePlayersWithPlaylist()
        self.assertEqual(VIDEO in apwpl, True)
        self.assertEqual(apwpl[VIDEO].playlist[0]
                         ["file"], timers[0].path)
        self.assertEqual(player.getVolume(), 80)
        self.assertEqual(player._getResumeStatus(VIDEO), None)

        schedulderaction.reset()

        # ------------ t6 ------------
        schedulderaction.calculate(
            timers, timedelta(minutes=self._t6))

        self.assertEqual(timers[0].active, False)
        self.assertEqual(timers[1].active, True)
        self.assertEqual(len(schedulderaction._getBeginningTimers()), 0)
        self.assertEqual(len(schedulderaction._getRunningTimers()), 1)
        self.assertEqual(len(schedulderaction._getEndingTimers()), 0)
        self.assertEqual(schedulderaction._getFader(), None)
        self.assertEqual(schedulderaction._getTimerToPlayAV(), None)
        self.assertEqual(schedulderaction._getTimerToStopAV(), None)
        self.assertEqual(schedulderaction._getTimerWithSystemAction(), None)
        

        schedulderaction.perform(timedelta(minutes=self._t6))

        apwpl = player.getActivePlayersWithPlaylist()
        self.assertEqual(VIDEO in apwpl, True)
        self.assertEqual(apwpl[VIDEO].playlist[0]
                         ["file"], timers[0].path)
        self.assertEqual(player.getVolume(), 80)
        self.assertEqual(player._getResumeStatus(VIDEO), None)

        schedulderaction.reset()

        # ------------ t7 ------------
        schedulderaction.calculate(
            timers, timedelta(minutes=self._t7))

        self.assertEqual(timers[0].active, False)
        self.assertEqual(timers[1].active, False)
        self.assertEqual(len(schedulderaction._getBeginningTimers()), 0)
        self.assertEqual(len(schedulderaction._getRunningTimers()), 0)
        self.assertEqual(len(schedulderaction._getEndingTimers()), 1)
        self.assertEqual(schedulderaction._getFader(), None)
        self.assertEqual(schedulderaction._getTimerToPlayAV(), None)
        self.assertEqual(schedulderaction._getTimerToStopAV(
        ).getTimer().id, timers[1].id)
        self.assertEqual(schedulderaction._getTimerWithSystemAction(), None)
        

        schedulderaction.perform(timedelta(minutes=self._t7))

        apwpl = player.getActivePlayersWithPlaylist()
        self.assertEqual(len(apwpl), 0)
        self.assertEqual(player.getVolume(), 80)
        self.assertEqual(player._getResumeStatus(AUDIO), None)
        self.assertEqual(player._getResumeStatus(VIDEO), None)
        self.assertEqual(player._getResumeStatus(PICTURE), None)

        schedulderaction.reset()

        # ------------ t8 ------------
        schedulderaction.calculate(
            timers, timedelta(minutes=self._t8))

        self.assertEqual(timers[0].active, False)
        self.assertEqual(timers[1].active, False)
        self.assertEqual(len(schedulderaction._getBeginningTimers()), 0)
        self.assertEqual(len(schedulderaction._getRunningTimers()), 0)
        self.assertEqual(len(schedulderaction._getEndingTimers()), 0)
        self.assertEqual(schedulderaction._getFader(), None)
        self.assertEqual(schedulderaction._getTimerToPlayAV(), None)
        self.assertEqual(schedulderaction._getTimerToStopAV(), None)
        self.assertEqual(schedulderaction._getTimerWithSystemAction(), None)
        

        schedulderaction.perform(timedelta(minutes=self._t8))

        apwpl = player.getActivePlayersWithPlaylist()
        self.assertEqual(len(apwpl), 0)
        self.assertEqual(player.getVolume(), 80)
        self.assertEqual(player._getResumeStatus(AUDIO), None)
        self.assertEqual(player._getResumeStatus(VIDEO), None)
        self.assertEqual(player._getResumeStatus(PICTURE), None)

        schedulderaction.reset()

    def test_tc_6_1_3(self):
        """
        Media 1 |---------|                            
        Timer 1           |------------------X
        Timer 2                      X-----------------S

        t       |----M1---|----T1----|-----------------|---------------->
                t0        t1    t2   t3  t4  t5   t6   t7   t8
        Player            play       stop              play
        """
        # ------------ setup player ------------
        player = MockPlayer()
        playlist = player._buildPlaylist(["Media M1"], VIDEO)
        player.setVolume(80)
        player.play(playlist)

        schedulderaction = SchedulerAction(player)

        # ------------ setup timers ------------
        # Timer 1 (T1)
        timer1 = Timer(1)
        timer1.label = "Timer 1"
        timer1.end_type = END_TYPE_DURATION
        timer1.duration_timedelta = timedelta(minutes=self._t5 - self._t1)
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
            Period(timedelta(minutes=self._t1), timedelta(minutes=self._t5))]

        # Timer 2 (T2)
        timer2 = Timer(2)
        timer2.label = "Timer 2"
        timer2.end_type = END_TYPE_DURATION
        timer2.duration_timedelta = timedelta(minutes=self._t7 - self._t3)
        timer2.media_action = MEDIA_ACTION_STOP_START
        timer2.path = "Media T2"
        timer2.media_type = VIDEO
        timer2.repeat = False
        timer2.resume = True
        timer2.fade = FADE_OFF
        timer2.vol_min = 0
        timer2.vol_max = 100
        timer2.system_action = SYSTEM_ACTION_NONE
        timer2.active = False
        timer2.notify = False
        timer2.periods = [
            Period(timedelta(minutes=self._t3), timedelta(minutes=self._t7))]

        timers = [timer1, timer2]

        # ------------ t0 ------------
        schedulderaction.calculate(
            timers, timedelta(minutes=self._t0))

        self.assertEqual(timers[0].active, False)
        self.assertEqual(timers[1].active, False)
        self.assertEqual(len(schedulderaction._getBeginningTimers()), 0)
        self.assertEqual(len(schedulderaction._getRunningTimers()), 0)
        self.assertEqual(len(schedulderaction._getEndingTimers()), 0)
        self.assertEqual(schedulderaction._getFader(), None)
        self.assertEqual(schedulderaction._getTimerToPlayAV(), None)
        self.assertEqual(schedulderaction._getTimerToStopAV(), None)
        self.assertEqual(schedulderaction._getTimerWithSystemAction(), None)
        

        schedulderaction.perform(timedelta(minutes=self._t0))

        apwpl = player.getActivePlayersWithPlaylist()
        self.assertEqual(VIDEO in apwpl, True)
        self.assertEqual(apwpl[VIDEO].playlist[0]["file"], "Media M1")
        self.assertEqual(player.getVolume(), 80)
        self.assertEqual(player._getResumeStatus(VIDEO), None)

        schedulderaction.reset()

        # ------------ t1 ------------
        schedulderaction.calculate(
            timers, timedelta(minutes=self._t1))

        self.assertEqual(timers[0].active, True)
        self.assertEqual(timers[1].active, False)
        self.assertEqual(len(schedulderaction._getBeginningTimers()), 1)
        self.assertEqual(len(schedulderaction._getRunningTimers()), 0)
        self.assertEqual(len(schedulderaction._getEndingTimers()), 0)
        self.assertEqual(schedulderaction._getFader(
        ).getTimer().id, timers[0].id)
        self.assertEqual(schedulderaction._getTimerToPlayAV(
        ).getTimer().id, timers[0].id)
        self.assertEqual(schedulderaction._getTimerToStopAV(), None)
        self.assertEqual(schedulderaction._getTimerWithSystemAction(), None)
        

        schedulderaction.perform(timedelta(minutes=self._t1))

        apwpl = player.getActivePlayersWithPlaylist()
        self.assertEqual(VIDEO in apwpl, True)
        self.assertEqual(apwpl[VIDEO].playlist[0]
                         ["file"], timers[0].path)
        self.assertEqual(player.getVolume(), 80)
        self.assertNotEqual(player._getResumeStatus(VIDEO), None)
        self.assertEqual(player._getResumeStatus(
            VIDEO)._timer.id, timers[0].id)
        self.assertEqual(player._getResumeStatus(
            VIDEO)._state.playlist[0]["file"], "Media M1")

        schedulderaction.reset()

        # ------------ t2 ------------
        schedulderaction.calculate(
            timers, timedelta(minutes=self._t2))

        self.assertEqual(timers[0].active, True)
        self.assertEqual(timers[1].active, False)
        self.assertEqual(len(schedulderaction._getBeginningTimers()), 0)
        self.assertEqual(len(schedulderaction._getRunningTimers()), 1)
        self.assertEqual(len(schedulderaction._getEndingTimers()), 0)
        self.assertEqual(schedulderaction._getFader(
        ).getTimer().id, timers[0].id)
        self.assertEqual(schedulderaction._getTimerToPlayAV(), None)
        self.assertEqual(schedulderaction._getTimerToStopAV(), None)
        self.assertEqual(schedulderaction._getTimerWithSystemAction(), None)
        

        schedulderaction.perform(timedelta(minutes=self._t2))

        apwpl = player.getActivePlayersWithPlaylist()
        self.assertEqual(VIDEO in apwpl, True)
        self.assertEqual(apwpl[VIDEO].playlist[0]
                         ["file"], timers[0].path)
        self.assertEqual(player.getVolume(), 72)
        self.assertNotEqual(player._getResumeStatus(VIDEO), None)
        self.assertEqual(player._getResumeStatus(
            VIDEO)._timer.id, timers[0].id)
        self.assertEqual(player._getResumeStatus(
            VIDEO)._state.playlist[0]["file"], "Media M1")

        schedulderaction.reset()

        # ------------ t3 ------------
        schedulderaction.calculate(
            timers, timedelta(minutes=self._t3))

        self.assertEqual(timers[0].active, True)
        self.assertEqual(timers[1].active, True)
        self.assertEqual(len(schedulderaction._getBeginningTimers()), 1)
        self.assertEqual(len(schedulderaction._getRunningTimers()), 1)
        self.assertEqual(len(schedulderaction._getEndingTimers()), 0)
        self.assertEqual(schedulderaction._getFader(
        ).getTimer().id, timers[0].id)
        self.assertEqual(schedulderaction._getTimerToPlayAV(), None)
        self.assertEqual(schedulderaction._getTimerToStopAV(
        ).getTimer().id, timers[1].id)
        self.assertEqual(schedulderaction._getTimerWithSystemAction(), None)
        

        schedulderaction.perform(timedelta(minutes=self._t3))

        apwpl = player.getActivePlayersWithPlaylist()
        self.assertEqual(len(apwpl), 0)
        self.assertEqual(player.getVolume(), 65)
        self.assertEqual(player._getResumeStatus(VIDEO), None)

        schedulderaction.reset()

        # ------------ t4 ------------
        schedulderaction.calculate(
            timers, timedelta(minutes=self._t4))

        self.assertEqual(timers[0].active, True)
        self.assertEqual(timers[1].active, True)
        self.assertEqual(len(schedulderaction._getBeginningTimers()), 0)
        self.assertEqual(len(schedulderaction._getRunningTimers()), 1)
        self.assertEqual(len(schedulderaction._getEndingTimers()), 0)
        self.assertEqual(schedulderaction._getFader(
        ).getTimer().id, timers[0].id)
        self.assertEqual(schedulderaction._getTimerToPlayAV(), None)
        self.assertEqual(schedulderaction._getTimerToStopAV(), None)
        self.assertEqual(schedulderaction._getTimerWithSystemAction(), None)
        

        schedulderaction.perform(timedelta(minutes=self._t4))

        apwpl = player.getActivePlayersWithPlaylist()
        self.assertEqual(len(apwpl), 0)
        self.assertEqual(player.getVolume(), 58)
        self.assertEqual(player._getResumeStatus(VIDEO), None)

        schedulderaction.reset()

        # ------------ t5 ------------
        schedulderaction.calculate(
            timers, timedelta(minutes=self._t5))

        self.assertEqual(timers[0].active, False)
        self.assertEqual(timers[1].active, True)
        self.assertEqual(len(schedulderaction._getBeginningTimers()), 0)
        self.assertEqual(len(schedulderaction._getRunningTimers()), 0)
        self.assertEqual(len(schedulderaction._getEndingTimers()), 1)
        self.assertEqual(schedulderaction._getFader(), None)
        self.assertEqual(schedulderaction._getTimerToPlayAV(), None)
        self.assertEqual(schedulderaction._getTimerToStopAV(
        ).getTimer().id, timers[0].id)
        self.assertEqual(schedulderaction._getTimerWithSystemAction(), None)
        

        schedulderaction.perform(timedelta(minutes=self._t5))

        apwpl = player.getActivePlayersWithPlaylist()
        self.assertEqual(len(apwpl), 0)
        self.assertEqual(player.getVolume(), 80)
        self.assertEqual(player._getResumeStatus(VIDEO), None)

        schedulderaction.reset()

        # ------------ t6 ------------
        schedulderaction.calculate(
            timers, timedelta(minutes=self._t6))

        self.assertEqual(timers[0].active, False)
        self.assertEqual(timers[1].active, True)
        self.assertEqual(len(schedulderaction._getBeginningTimers()), 0)
        self.assertEqual(len(schedulderaction._getRunningTimers()), 0)
        self.assertEqual(len(schedulderaction._getEndingTimers()), 0)
        self.assertEqual(schedulderaction._getFader(), None)
        self.assertEqual(schedulderaction._getTimerToPlayAV(), None)
        self.assertEqual(schedulderaction._getTimerToStopAV(), None)
        self.assertEqual(schedulderaction._getTimerWithSystemAction(), None)
        

        schedulderaction.perform(timedelta(minutes=self._t6))

        apwpl = player.getActivePlayersWithPlaylist()
        self.assertEqual(len(apwpl), 0)
        self.assertEqual(player.getVolume(), 80)
        self.assertEqual(player._getResumeStatus(VIDEO), None)

        schedulderaction.reset()

        # ------------ t7 ------------
        schedulderaction.calculate(
            timers, timedelta(minutes=self._t7))

        self.assertEqual(timers[0].active, False)
        self.assertEqual(timers[1].active, False)
        self.assertEqual(len(schedulderaction._getBeginningTimers()), 0)
        self.assertEqual(len(schedulderaction._getRunningTimers()), 0)
        self.assertEqual(len(schedulderaction._getEndingTimers()), 1)
        self.assertEqual(schedulderaction._getFader(), None)
        self.assertEqual(schedulderaction._getTimerToPlayAV(
        ).getTimer().id, timers[1].id)
        self.assertEqual(schedulderaction._getTimerToStopAV(), None)
        self.assertEqual(schedulderaction._getTimerWithSystemAction(), None)
        

        schedulderaction.perform(timedelta(minutes=self._t7))

        apwpl = player.getActivePlayersWithPlaylist()
        self.assertEqual(VIDEO in apwpl, True)
        self.assertEqual(apwpl[VIDEO].playlist[0]
                         ["file"], timers[1].path)
        self.assertEqual(player.getVolume(), 80)
        self.assertEqual(player._getResumeStatus(AUDIO), None)
        self.assertEqual(player._getResumeStatus(VIDEO), None)
        self.assertEqual(player._getResumeStatus(PICTURE), None)

        schedulderaction.reset()

        # ------------ t8 ------------
        schedulderaction.calculate(
            timers, timedelta(minutes=self._t8))

        self.assertEqual(timers[0].active, False)
        self.assertEqual(timers[1].active, False)
        self.assertEqual(len(schedulderaction._getBeginningTimers()), 0)
        self.assertEqual(len(schedulderaction._getRunningTimers()), 0)
        self.assertEqual(len(schedulderaction._getEndingTimers()), 0)
        self.assertEqual(schedulderaction._getFader(), None)
        self.assertEqual(schedulderaction._getTimerToPlayAV(), None)
        self.assertEqual(schedulderaction._getTimerToStopAV(), None)
        self.assertEqual(schedulderaction._getTimerWithSystemAction(), None)
        

        schedulderaction.perform(timedelta(minutes=self._t8))

        apwpl = player.getActivePlayersWithPlaylist()
        self.assertEqual(VIDEO in apwpl, True)
        self.assertEqual(apwpl[VIDEO].playlist[0]
                         ["file"], timers[1].path)
        self.assertEqual(player.getVolume(), 80)
        self.assertEqual(player._getResumeStatus(AUDIO), None)
        self.assertEqual(player._getResumeStatus(VIDEO), None)
        self.assertEqual(player._getResumeStatus(PICTURE), None)
