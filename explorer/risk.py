
SEISMIC_INTENSITY_SCALE = {
    # PGA, Peak Ground Acceleration (cm/sec^2), is a measure of the maximum acceleration experienced by the ground during an earthquake.
    # PGV, Peak Ground Velocity (cm/sec), measures the maximum ground velocity during an earthquake.
    # source: https://zh.wikipedia.org/zh-tw/%E4%BA%A4%E9%80%9A%E9%83%A8%E4%B8%AD%E5%A4%AE%E6%B0%A3%E8%B1%A1%E7%BD%B2%E5%9C%B0%E9%9C%87%E9%9C%87%E5%BA%A6%E5%88%86%E7%B4%9A
    "0級": {"intensity": "0", "scale": "Micro", "PGA": {"lower": 0, "upper": 0.8}, "PGV": {"lower": 0, "upper": 0.2}},
    "1級": {"intensity": "1", "scale": "Very minor", "PGA": {"lower": 0.8, "upper": 2.5}, "PGV": {"lower": 0.2, "upper": 0.7}},
    "2級": {"intensity": "2", "scale": "Minor", "PGA": {"lower": 2.5, "upper": 8}, "PGV": {"lower": 0.7, "upper": 1.9}},
    "3級": {"intensity": "3", "scale": "Light", "PGA": {"lower": 8, "upper": 25}, "PGV": {"lower": 1.9, "upper": 5.7}},
    "4級": {"intensity": "4", "scale": "Moderate", "PGA": {"lower": 25, "upper": 80}, "PGV": {"lower": 5.7, "upper": 15}},
    "5弱": {"intensity": "5-", "scale": "Strong", "PGA": {"lower": 80, "upper": 140}, "PGV": {"lower": 15, "upper": 30}},
    "5強": {"intensity": "5+", "scale": "Strong", "PGA": {"lower": 140, "upper": 250}, "PGV": {"lower": 30, "upper": 50}},
    "6弱": {"intensity": "6-", "scale": "Very strong", "PGA": {"lower": 250, "upper": 440}, "PGV": {"lower": 50, "upper": 80}},
    "6強": {"intensity": "6+", "scale": "Very strong", "PGA": {"lower": 440, "upper": 800}, "PGV": {"lower": 80, "upper": 140}},
    "7級": {"intensity": "7", "scale": "Great", "PGA": {"lower": 800, "upper": "unlimited"}, "PGV": {"lower": 140, "upper": "unlimited"}}
}