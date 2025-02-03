# RTC Clock DS1302
# https://github.com/omarbenhamid/micropython-ds1302-rtc

from machine import Pin

class DS1302:
    DS1302_REG_SECOND = (0x80)
    DS1302_REG_MINUTE = (0x82)
    DS1302_REG_HOUR   = (0x84)
    DS1302_REG_DAY    = (0x86)
    DS1302_REG_MONTH  = (0x88)
    DS1302_REG_WEEKDAY= (0x8A)
    DS1302_REG_YEAR   = (0x8C)
    DS1302_REG_WP     = (0x8E)
    DS1302_REG_CTRL   = (0x90)
    DS1302_REG_RAM    = (0xC0)
    
    CLK_PIN = 23
    DAT_PIN = 18
    RST_PIN = 19
    
    def __init__(self, clk=CLK_PIN, dat=DAT_PIN, rst=RST_PIN):
        self.clk = Pin(clk)
        self.dat = Pin(dat)
        self.rst = Pin(rst)
        self.clk.init(Pin.OUT)
        self.rst.init(Pin.OUT)
        self.start()

    def _dec2hex(self, dat):
        return (dat//10) * 16 + (dat % 10)

    def _hex2dec(self, dat):
        return (dat//16) * 10 + (dat % 16)

    def _write_byte(self, dat):
        self.dat.init(Pin.OUT)
        for i in range(8):
            self.dat.value((dat >> i) & 1)
            self.clk.value(1)
            self.clk.value(0)

    def _read_byte(self):
        d = 0
        self.dat.init(Pin.IN)
        for i in range(8):
            d = d | (self.dat.value() << i)
            self.clk.value(1)
            self.clk.value(0)
        return d

    def _get_reg(self, reg):
        self.rst.value(1)
        self._write_byte(reg)
        t = self._read_byte()
        self.rst.value(0)
        return t

    def _set_reg(self, reg, dat):
        self.rst.value(1)
        self._write_byte(reg)
        self._write_byte(dat)
        self.rst.value(0)

    def _wr(self, reg, dat):
        self._set_reg(self.DS1302_REG_WP, 0)
        self._set_reg(reg, dat)
        self._set_reg(self.DS1302_REG_WP, 0x80)

    def start(self):
        t = self._get_reg(self.DS1302_REG_SECOND + 1)
        self._wr(self.DS1302_REG_SECOND, t & 0x7f)

    def stop(self):
        t = self._get_reg(self.DS1302_REG_SECOND + 1)
        self._wr(self.DS1302_REG_SECOND, t | 0x80)

    def second(self, second=None):
        if second == None:
            return self._hex2dec(self._get_reg(self.DS1302_REG_SECOND+1)) % 60
        else:
            self._wr(self.DS1302_REG_SECOND, self._dec2hex(second % 60))

    def minute(self, minute=None):
        if minute == None:
            return self._hex2dec(self._get_reg(self.DS1302_REG_MINUTE+1))
        else:
            self._wr(self.DS1302_REG_MINUTE, self._dec2hex(minute % 60))

    def hour(self, hour=None):
        if hour == None:
            return self._hex2dec(self._get_reg(self.DS1302_REG_HOUR+1))
        else:
            self._wr(self.DS1302_REG_HOUR, self._dec2hex(hour % 24))

    def weekday(self, weekday=None):
        if weekday == None:
            return self._hex2dec(self._get_reg(self.DS1302_REG_WEEKDAY+1))
        else:
            self._wr(self.DS1302_REG_WEEKDAY, self._dec2hex(weekday % 8))

    def day(self, day=None):
        if day == None:
            return self._hex2dec(self._get_reg(self.DS1302_REG_DAY+1))
        else:
            self._wr(self.DS1302_REG_DAY, self._dec2hex(day % 32))

    def month(self, month=None):
        if month == None:
            return self._hex2dec(self._get_reg(self.DS1302_REG_MONTH+1))
        else:
            self._wr(self.DS1302_REG_MONTH, self._dec2hex(month % 13))

    def year(self, year=None):
        if year == None:
            return self._hex2dec(self._get_reg(self.DS1302_REG_YEAR+1)) + 2000
        else:
            self._wr(self.DS1302_REG_YEAR, self._dec2hex(year % 100))

    def date_time(self, dat=None):
        if dat == None:
            return [self.year(), self.month(), self.day(), self.weekday(), self.hour(), self.minute(), self.second()]
        else:
            self.year(dat[0])
            self.month(dat[1])
            self.day(dat[2])
            self.weekday(dat[3])
            self.hour(dat[4])
            self.minute(dat[5])
            self.second(dat[6])

    def ram(self, reg, dat=None):
        if dat == None:
            return self._get_reg(self.DS1302_REG_RAM + 1 + (reg % 31)*2)
        else:
            self._wr(self.DS1302_REG_RAM + (reg % 31)*2, dat)

    def weekday_string(self, weekday):
        return ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"][weekday]