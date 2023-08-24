from functools import reduce


class Channel:
    def __init__(self, name, mhz):
        self.name = name
        self.mhz = mhz

    def get_mhz(self):
        return self.mhz

    def __repr__(self):
        return f"{self.name} [{self.mhz}]"

    def __str__(self):
        return self.name


all_channels = [
    Channel("R1", 5658),
    Channel("R2", 5695),
    Channel("R3", 5732),
    Channel("R4", 5769),
    Channel("R5", 5806),
    Channel("R6", 5843),
    Channel("R7", 5880),
    Channel("R8", 5917),

    Channel("F1", 5740),
    Channel("F2", 5760),
    Channel("F3", 5780),
    Channel("F4", 5800),
    Channel("F5", 5820),
    Channel("F6", 5840),
    Channel("F7", 5860),

    Channel("E1", 5705),
    Channel("E2", 5685),
    Channel("E3", 5665),
    Channel("E5", 5885),
    Channel("E6", 5905),

    Channel("B1", 5733),
    Channel("B2", 5752),
    Channel("B3", 5771),
    Channel("B4", 5790),
    Channel("B5", 5809),
    Channel("B6", 5828),
    Channel("B7", 5847),
    Channel("B8", 5866),

    Channel("A8", 5725),
    Channel("A7", 5745),
    Channel("A6", 5765),
    Channel("A5", 5785),
    Channel("A4", 5805),
    Channel("A3", 5825),
    Channel("A2", 5845),
    Channel("A1", 5865),
]


class ChannelFinder:
    def __init__(self, pilots, min_gap_between_channels_mhz, min_gap_between_channel_and_harmonic_mhz,
                 min_gap_between_channel_and_imd_peak_mhz):
        self.pilots = pilots
        self.min_gap_between_channels_mhz = min_gap_between_channels_mhz
        self.min_gap_between_channel_and_harmonic_mhz = min_gap_between_channel_and_harmonic_mhz
        self.min_gap_between_channel_and_imd_peak_mhz = min_gap_between_channel_and_imd_peak_mhz

    def find_channels(self):
        good_channel_sets = self._find_channels(
            self.pilots,
            self.min_gap_between_channels_mhz,
            self.min_gap_between_channel_and_harmonic_mhz,
            self.min_gap_between_channel_and_imd_peak_mhz
        )

        if len(good_channel_sets) == 0:
            print("No channels sets satisfying requirements were found")
        else:
            print("Found following channels sets satisfying requirements")
            for channels in good_channel_sets:
                print(", ".join(str(channel) for channel in channels))

    def _find_channels(self, pilots, channel_gap, harmonics_gap, imd_gap):
        pilots_channels = [0] * pilots
        check = ChannelCheck(channel_gap, imd_gap, harmonics_gap)
        self._append_channel(0, 0, pilots_channels, check)

        return check.good_sets

    def _append_channel(self, pilot, min_channel, pilots_channels, channel_check):
        for channel in range(min_channel, len(all_channels)):
            pilots_channels[pilot] = channel
            if pilot < len(pilots_channels) - 1:
                self._append_channel(pilot + 1, channel + 1, pilots_channels, channel_check)
            else:
                channel_check.is_enough_separation(pilots_channels)


class ChannelCheck:
    def __init__(self, channel_gap, imd_gap, harmonics_gap):
        self.channel_gap = channel_gap
        self.imd_gap = imd_gap
        self.harmonics_gap = harmonics_gap
        self.counter = 0
        self.good_sets = []

    def factorial(self, n):
        return reduce(lambda a, i: a * (i + 1), range(n), 1)

    def is_enough_separation(self, pilots_channels):
        self.counter += 1
        if self.counter % 1000000 == 0:
            total_combinations = self.factorial(len(all_channels)) // (
                    self.factorial(len(all_channels) - len(pilots_channels)) * self.factorial(len(pilots_channels)))
            print("Progress: {:.2f}%".format(100.0 * self.counter / total_combinations))

        channel_set = [list(all_channels)[index] for index in pilots_channels]

        intervals = []

        channels = channel_set.copy()
        for i in range(len(channels) - 1):
            for j in range(i + 1, len(channels)):
                c1 = channels[i]
                c2 = channels[j]
                imd1 = c1.get_mhz() * 2 - c2.get_mhz()
                imd2 = c2.get_mhz() * 2 - c1.get_mhz()
                intervals.append(
                    IntervalMhz(imd1 - self.imd_gap, imd1 + self.imd_gap, str(c1) + "+" + str(c2) + " IMD"))
                intervals.append(
                    IntervalMhz(imd2 - self.imd_gap, imd2 + self.imd_gap, str(c2) + "+" + str(c1) + " IMD"))

        intervals.extend([IntervalMhz(channel.get_mhz() + 190 - self.harmonics_gap,
                                      channel.get_mhz() + 190 + self.harmonics_gap, str(channel) + " 190 harmonics") for
                          channel in channel_set])
        intervals.extend([IntervalMhz(channel.get_mhz() + 240 - self.harmonics_gap,
                                      channel.get_mhz() + 240 + self.harmonics_gap, str(channel) + " 240 harmonics") for
                          channel in channel_set])

        for i in range(len(channel_set) - 1):
            for j in range(i + 1, len(channel_set)):
                if abs(channel_set[i].get_mhz() - channel_set[j].get_mhz()) < self.channel_gap:
                    return False

        for channel in channel_set:
            for interval in intervals:
                if interval.includes(channel.get_mhz()):
                    return False

        self.good_sets.append(channel_set)
        return True


class IntervalMhz:
    def __init__(self, start, end, info):
        self.start = start
        self.end = end
        self.info = info

    def includes(self, mhz):
        return self.start <= mhz <= self.end

    def __str__(self):
        return "{}-{} : {}".format(self.start, self.end, self.info)


if __name__ == "__main__":
    """
    7 pilots 26/11/11
    R7 R8 F2 F4 E1 E3 B6
    
    6 pilots 37/16/14
    R1 R2 R4 R8 B6 A1
    R1 R2 R8 B3 B6 A1
    
    6 pilots 35/11/16
    R1 R2 R4 R8 F7 A3
    
    6 pilots 25/17/17
    R1 R7 R8 F4 B2 A3
    
    5 pilots 38/19/18
    R2, F7, E6, B2, B4
    R2, E6, B2, B4, A1
    
    5 pilots 30/17/26
    R1 R2 R8 F5 B3
    
    4 pilots using only Raceband 37/41/36
    R1, R2, R4, R5
    
    4 pilots using only Raceband 40/34/34
    R7, F6, A8, A6    
    """
    # pilots = 4
    # minGapBetweenChannelsMhz = 30
    # minGapBetweenChannelAndHarmonicMhz = 25
    # minGapBetweenChannelAndImdPeakMhz = 25
    pilots = 4
    minGapBetweenChannelsMhz = 40
    minGapBetweenChannelAndHarmonicMhz = 34
    minGapBetweenChannelAndImdPeakMhz = 34

    finder = ChannelFinder(
        pilots,
        minGapBetweenChannelsMhz,
        minGapBetweenChannelAndHarmonicMhz,
        minGapBetweenChannelAndImdPeakMhz
    )
    finder.find_channels()
