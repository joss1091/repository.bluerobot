# -*- coding: utf-8 -*-

import os
import re
import datetime
import xbmc, xbmcgui, xbmcaddon

ADDON = xbmcaddon.Addon()
ADDONNAME = ADDON.getAddonInfo('id')
ADDONPATH = xbmc.translatePath(ADDON.getAddonInfo('path'))
LOC = ADDON.getLocalizedString

# ICON_DEFAULT = os.path.join(ADDONPATH, 'resources', 'media', 'pawprint.png')
# ICON_ERROR = os.path.join(ADDONPATH, 'resources', 'media', 'pawprint_red.png')

LANGOFFSET = 32130
msgdialogprogress = xbmcgui.DialogProgress()


def notifyLog(message, level=xbmc.LOGDEBUG):
    xbmc.log('[%s] %s' % (ADDONNAME, message.encode('utf-8')), level)

# def notifyUser(message, icon=ICON_DEFAULT, time=3000):
#     xbmcgui.Dialog().notification(LOC(32100), message.encode('utf-8'), icon, time)

class XBMCMonitor(xbmc.Monitor):

    def __init__(self, *args, **kwargs):
        xbmc.Monitor.__init__(self)
        self.SettingsChanged = False

    def onSettingsChanged(self):
        self.SettingsChanged = True


    @classmethod
    def onNotification(cls, sender, method, data):
        notifyLog('Notification triggered')
        notifyLog('sender: %s' % (sender))
        notifyLog('method: %s' % (method))
        notifyLog('data:   %s' % (data))

class SleepyWatchdog(XBMCMonitor):

    def __init__(self):

        self.currframe = 0
        self.wd_status = False

        XBMCMonitor.__init__(self)
        self.getWDSettings()

    def getWDSettings(self):

        self.mode = ADDON.getSetting('mode')
        self.notifyUser = True if ADDON.getSetting('showPopup').upper() == 'TRUE' else False

        # self.notificationTime = int(re.match('\d+', ADDON.getSetting('notificationTime')).group())

        self.notificationTime = int(re.findall('([0-9]+)', ADDON.getSetting('notificationTime'))[0]) \
            if len(re.findall('([0-9]+)', ADDON.getSetting('notificationTime'))) else 0

        self.sendCEC = True if ADDON.getSetting('sendCEC').upper() == 'TRUE' else False

        self.timeframe = False if ADDON.getSetting('timeframe') == '0' else True

        self.act_start = int(datetime.timedelta(hours=int(ADDON.getSetting('start'))).total_seconds())
        self.act_stop = int(datetime.timedelta(hours=int(ADDON.getSetting('stop'))).total_seconds())

        # self.maxIdleTime = int(re.match('\d+', ADDON.getSetting('maxIdleTime')).group()) * 60
        # self.userIdleTime = int(re.match('\d+', ADDON.getSetting('userIdleTime')).group()) * 60

        self.maxIdleTime = int(re.findall('([0-9]+)', ADDON.getSetting('maxIdleTime'))[0]) * 60 \
            if len(re.findall('([0-9]+)', ADDON.getSetting('maxIdleTime'))) else 0
        self.userIdleTime = int(re.findall('([0-9]+)', ADDON.getSetting('userIdleTime'))[0]) \
            if len(re.findall('([0-9]+)', ADDON.getSetting('userIdleTime'))) else 0

        self.action = int(ADDON.getSetting('action')) + LANGOFFSET
        self.jumpMainMenu = True if ADDON.getSetting('mainmenu').upper() == 'TRUE' else False
        self.keepAlive = True if ADDON.getSetting('keepalive').upper() == 'TRUE' else False
        self.addon_id = ADDON.getSetting('addon_id')

        self.testConfig = True if ADDON.getSetting('testConfig').upper() == 'TRUE' else False

        if self.act_stop > self.act_start:
            if (self.act_stop - self.act_start) <= self.maxIdleTime: xbmcgui.Dialog().ok(LOC(32100), LOC(32116))
        else:
            if (86400 + self.act_stop - self.act_start) <= self.maxIdleTime: xbmcgui.Dialog().ok(LOC(32100), LOC(32116))

        self.SettingsChanged = False

        notifyLog('settings (re)loaded...')
        notifyLog('current mode:             %s' % (self.mode))
        notifyLog('notify user:              %s' % (self.notifyUser))
        notifyLog('Duration of notification: %s' % (self.notificationTime))
        notifyLog('send CEC:                 %s' % (self.sendCEC))
        notifyLog('Time frame:               %s' % (self.timeframe))
        notifyLog('Activity start:           %s' % (self.act_start))
        notifyLog('Activity stop:            %s' % (self.act_stop))
        notifyLog('max. idle time:           %s' % (self.maxIdleTime))
        notifyLog('Idle time set by user:    %s' % (self.userIdleTime))
        notifyLog('Action:                   %s' % (self.action))
        notifyLog('Jump to main menue:       %s' % (self.jumpMainMenu))
        notifyLog('Keep alive:               %s' % (self.keepAlive))
        notifyLog('Run addon:                %s' % (self.addon_id))
        notifyLog('Test configuration:       %s' % (self.testConfig))

        if self.testConfig:
            self.maxIdleTime = 60 + int(self.notifyUser)*self.notificationTime
            notifyLog('running in test mode for %s secs' % (self.maxIdleTime))

    # user defined actions

    def stopVideoAudioTV(self):
        if xbmc.Player().isPlaying():
            notifyLog('media is playing, stopping it')
            xbmc.Player().stop()
            if self.jumpMainMenu:
                xbmc.sleep(500)
                notifyLog('jump to main menu')
                xbmc.executebuiltin('ActivateWindow(home)')

    @classmethod
    def quit(cls):
        notifyLog('quit kodi')
        xbmc.executebuiltin('Quit')

    @classmethod
    def systemReboot(cls):
        notifyLog('init system reboot')
        xbmc.restart()

    @classmethod
    def systemShutdown(cls):
        notifyLog('init system shutdown')
        xbmc.shutdown()

    @classmethod
    def systemHibernate(cls):
        notifyLog('init system hibernate')
        xbmc.executebuiltin('Hibernate')

    @classmethod
    def systemSuspend(cls):
        notifyLog('init system suspend')
        xbmc.executebuiltin('Suspend')

    def sendCecCommand(self):
        if not self.sendCEC: return
        notifyLog('send standby command via CEC')
        xbmc.executebuiltin('CECStandby')

    def runAddon(self):
        if xbmc.getCondVisibility('System.HasAddon(%s)' % (self.addon_id.split(',')[0])):
            notifyLog('run addon \'%s\'' % (self.addon_id))
            xbmc.executebuiltin('RunAddon(%s)' % (self.addon_id))
        else:
            notifyLog('could not run nonexistent addon \'%s\'' % (self.addon_id.split(',')[0]), level=xbmc.LOGERROR)

    def start(self):

        _currentIdleTime = 0
        _maxIdleTime = self.maxIdleTime

        while not xbmc.Monitor.abortRequested(self):
            self.actionCanceled = False

            _status = False
            if not self.timeframe or self.mode == 'USER':
                _status = True
            else:
                _currframe = (datetime.datetime.now() - datetime.datetime.now().replace(hour=0, minute=0, second=0,
                                                                                        microsecond=0)).seconds
                if self.act_start < self.act_stop:
                    if self.act_start <= _currframe < self.act_stop: _status = True
                else:
                    if self.act_start <= _currframe < 86400 or 0 <= _currframe < self.act_stop: _status = True

            if self.wd_status ^ _status:
                notifyLog('Watchdog status changed: %s' % ('active' if _status else 'inactive'))
                self.wd_status = _status

            if self.wd_status and _currentIdleTime > 60 and not self.testConfig:
                notifyLog('idle time: %s' % (str(datetime.timedelta(seconds=_currentIdleTime))))

            if _currentIdleTime > xbmc.getGlobalIdleTime():
                notifyLog('user activity detected, reset idle time')
                _maxIdleTime = self.maxIdleTime if self.mode == 'SERVICE' else self.userIdleTime
                _currentIdleTime = 0

            # Check if GlobalIdle longer than maxIdle and we're in a time frame

            if self.wd_status or self.testConfig:
                if _currentIdleTime > (_maxIdleTime - int(self.notifyUser)*self.notificationTime):

                    notifyLog('max idle time reached, ready to perform some action')

                    # Check if notification is allowed
                    if self.notifyUser and xbmc.Player().isPlaying():
                        count = 0
                        notifyLog('init notification countdown for action no. %s' % (self.action))
                        ret = msgdialogprogress.create(LOC(32203),LOC(32204))
                        secs = 0
                        percent = 0
                        increment = 100*100 / self.notificationTime
                        while (secs < self.notificationTime):
                            secs += 1
                            percent = increment*secs / 100
                            sec_left = str((self.notificationTime - secs))
                            remaining_display = str(sec_left)
                            msgdialogprogress.update(percent, LOC(32204), remaining_display)
                            # xbmc.sleep(1000)
                            if msgdialogprogress.iscanceled():
                                self.actionCanceled = True
                                break
                            # notifyUser(LOC(32115) % (LOC(self.action), self.notificationTime - count), time=7000)
                            if xbmc.Monitor.waitForAbort(self, 1): break

                            if _currentIdleTime > xbmc.getGlobalIdleTime():
                                self.actionCanceled = True
                                break

                    if not self.actionCanceled:

                        self.sendCecCommand()
                        {
                        32130: self.stopVideoAudioTV,
                        32131: self.systemReboot,
                        32132: self.systemShutdown,
                        32133: self.systemHibernate,
                        32134: self.systemSuspend,
                        32135: self.runAddon,
                        32136: self.quit
                        }.get(self.action)()
                        #
                        # ToDo: implement more user defined actions here
                        #       Action numbers are defined in settings.xml/strings.xml
                        #       also see LANGOFFSET
                        #
                        msgdialogprogress.close()
                        if self.testConfig:
                            notifyLog('watchdog was running in test mode, keep it alive')
                        else:
                            if self.keepAlive:
                                notifyLog('keep watchdog alive, update idletime for next cycle')
                                _maxIdleTime += self.maxIdleTime
                            else:
                                break
                    else:
                        notifyLog('Countdown canceled by user action')
                        # notifyUser(LOC(32118), icon=ICON_ERROR)
                        msgdialogprogress.close()

                    # Reset test status
                    # if self.testConfig:
                    #     ADDON.setSetting('testConfig', 'false')

            _loop = 0
            while not xbmc.Monitor.waitForAbort(self, 15):
                _loop += 15
                _currentIdleTime += 15

                if self.SettingsChanged:
                    notifyLog('settings changed')
                    self.getWDSettings()
                    _maxIdleTime = self.maxIdleTime
                    break

                if self.testConfig or _currentIdleTime > xbmc.getGlobalIdleTime() or _loop >= 60: break

# MAIN #

if __name__ == '__main__':

    mode = 'SERVICE'
    ADDON.setSetting('mode', mode)
    WatchDog = SleepyWatchdog()
    try:
        notifyLog('Sleep Playback kicks in (mode: %s)' % mode)
        WatchDog.start()
    except Exception, e:
        notifyLog(e.message, level=xbmc.LOGERROR)

    notifyLog('Sleep Playback kicks off from mode: %s' % WatchDog.mode)
    del WatchDog
    ADDON.setSetting('mode', mode)
