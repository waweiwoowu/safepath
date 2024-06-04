
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

class SeismicIntensityScale:
    def __init__(self, intensity):
        if intensity in list(SEISMIC_INTENSITY_SCALE.keys()):
            self.pga_lower = SEISMIC_INTENSITY_SCALE[intensity]["PGA"]["lower"]
            # self.pga_upper = SEISMIC_INTENSITY_SCALE[intensity]["PGA"]["upper"]
            # self.pga_average = (self.lower + self.upper) / 2
            self.pgv_lower = SEISMIC_INTENSITY_SCALE[intensity]["PGV"]["lower"]
            # self.pgv_upper = SEISMIC_INTENSITY_SCALE[intensity]["PGV"]["upper"]
            # self.pgv_average = (self.lower + self.upper) / 2
        elif intensity == "5級":
            self.pga_lower = (SEISMIC_INTENSITY_SCALE["5弱"]["PGA"]["lower"] + 
                              SEISMIC_INTENSITY_SCALE["5強"]["PGA"]["lower"]) / 2
            self.pgv_lower = (SEISMIC_INTENSITY_SCALE["5弱"]["PGV"]["lower"] + 
                              SEISMIC_INTENSITY_SCALE["5強"]["PGV"]["lower"]) / 2
        elif intensity == "6級":
            self.pga_lower = (SEISMIC_INTENSITY_SCALE["6弱"]["PGA"]["lower"] + 
                              SEISMIC_INTENSITY_SCALE["6強"]["PGA"]["lower"]) / 2
            self.pgv_lower = (SEISMIC_INTENSITY_SCALE["6弱"]["PGV"]["lower"] + 
                              SEISMIC_INTENSITY_SCALE["6強"]["PGV"]["lower"]) / 2
        else:
            self.pga_lower = self.pgv_lower = None
            
def pgv_lower_to_intensity(pgv_lower):
    pgv_lowers = pgv_lower
    if type(pgv_lowers) != list:
        pgv_lowers = []
        pgv_lowers.append(pgv_lower)
    pgv_lower = 0
    for pgv in pgv_lowers:
        pgv_lower += pgv
    pgv_lower /= len(pgv_lowers)
    
    if pgv_lower >= SEISMIC_INTENSITY_SCALE["7級"]["PGV"]["lower"]:
        return "7級"
    elif pgv_lower >= SEISMIC_INTENSITY_SCALE["6強"]["PGV"]["lower"]:
        return "6強"
    elif pgv_lower >= SEISMIC_INTENSITY_SCALE["6弱"]["PGV"]["lower"]:
        return "6弱"
    elif pgv_lower >= SEISMIC_INTENSITY_SCALE["5強"]["PGV"]["lower"]:
        return "5強"
    elif pgv_lower >= SEISMIC_INTENSITY_SCALE["5弱"]["PGV"]["lower"]:
        return "5弱"
    elif pgv_lower >= SEISMIC_INTENSITY_SCALE["4級"]["PGV"]["lower"]:
        return "4級"
    elif pgv_lower >= SEISMIC_INTENSITY_SCALE["3級"]["PGV"]["lower"]:
        return "3級"
    elif pgv_lower >= SEISMIC_INTENSITY_SCALE["2級"]["PGV"]["lower"]:
        return "2級"
    elif pgv_lower >= SEISMIC_INTENSITY_SCALE["1級"]["PGV"]["lower"]:
        return "1級"
    elif pgv_lower >= SEISMIC_INTENSITY_SCALE["0級"]["PGV"]["lower"]:
        return "0級"
    else:
        return "error"

def intensity_to_pgv_lower(intensity):
    intensities = intensity
    if type(intensities) != list:
        intensities = []
        intensities.append(intensity)
    energy = 0
    for intensity in intensities:
        scale = SeismicIntensityScale(intensity)
        energy += scale.pgv_lower ** 2
    return (energy / len(intensities)) ** 0.5


if __name__ == "__main__":
    intensity = "5級"
    # scale = SeismicIntensityScale(intensity)
    # print(scale.pgv_lower)
    print(intensity_to_pgv_lower(intensity))
    intensity_list = ["0級", "1級", "2級", "3級", "4級", "5弱", "5強", "6弱", "6強", "7級"]
    print(intensity_to_pgv_lower(intensity_list))
    
    pgv_lower = 22.5
    print(pgv_lower_to_intensity(pgv_lower))
    pgv_lower_list = [1, 2, 3, 4, 60]
    print(pgv_lower_to_intensity(pgv_lower_list))

