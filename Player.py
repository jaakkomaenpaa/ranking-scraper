"""
A class for handling Player objects
"""

# NOT USED
def get_next_week(current):
    [year, week] = current.split('-')
    year = int(year)
    week = int(week)
    if week >= 52:
        return f"{year}-1"
    return f"{year}-{week + 1}"

# Returns a dict where week number is the key for that week's points
def get_points_by_week(weeks, points):
    return {key: value for key, value in zip(weeks, points)}


def sort_list_by_week(item):
    return int(item.split('-')[1])


class Player:
    """
    name: string, player name
    abbreviation: string, abbreviation of represented country
    confederation: string, confederation name
    weeks: list, the weeks that the player has points from
    points: list, the points that the player has

    the weeks and their corresponding points are stored in separate lists,
    but in the same order (in the same index)
    """
    def __init__(self, name, abbreviation, confederation, weeks, points):
        self.__name = name
        self.__abbreviation = abbreviation
        self.__confederation = confederation
        self.__weeks = weeks
        self.__points = points

    def get_name(self):
        return self.__name

    def get_abbreviation(self):
        return self.__abbreviation

    def get_confederation(self):
        return self.__confederation

    def get_weeks(self):
        return self.__weeks

    def get_points(self):
        return self.__points

    def add_weeks(self, weeks):
        self.__weeks.insert(0, weeks)

    def add_points(self, points):
        self.__points.insert(0, points)

    # Returns a list of player data, which will be converted to a csv row
    def get_csv_row(self):

        csv_row = [self.__abbreviation, self.__name]
        points = get_points_by_week(self.__weeks, self.__points)
        weeks = sorted(self.__weeks, key=sort_list_by_week)

        # Adding points under corresponding weeks
        current_week = 1
        for _ in range(1, 53):
            # If player has points for current week, add them under it
            # If not, add an empty cell
            if len(weeks) != 0 and int(weeks[0].split('-')[1]) == current_week:
                csv_row.append(points[weeks[0]])
                weeks.pop(0)
            else:
                csv_row.append('')
            current_week += 1

        # Reserve cell space for OVR calculation, for example
        for _ in range(1, 4):
            csv_row.append('')

        csv_row.append(self.__confederation)

        return csv_row
