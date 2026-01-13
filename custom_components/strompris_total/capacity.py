from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple

@dataclass
class HourBucket:
    start: datetime
    sum_kw: float = 0.0
    n: int = 0

    def add(self, kw: float) -> None:
        self.sum_kw += kw
        self.n += 1

    @property
    def avg_kw(self) -> float:
        return self.sum_kw / self.n if self.n else 0.0


class CapacityCalculator:
    """Tracks hourly average kW, daily max (døgnmaks), and top-3 daily maxima in current month."""

    def __init__(self) -> None:
        self.current_hour: Optional[HourBucket] = None
        self.current_day: Optional[datetime.date] = None
        self.day_max_kw: float = 0.0
        self.daily_max_by_date: Dict[str, float] = {}  # "YYYY-MM-DD" -> døgnmaks (kW)

    def _hour_start(self, t: datetime) -> datetime:
        return t.replace(minute=0, second=0, microsecond=0)

    def _date_key(self, d) -> str:
        return d.isoformat()

    def update(self, t: datetime, kw: float) -> None:
        """Call on each power update."""
        if t.tzinfo is None:
            t = t.replace(tzinfo=timezone.utc)

        hour_start = self._hour_start(t)
        day = t.date()

        # init
        if self.current_hour is None:
            self.current_hour = HourBucket(start=hour_start)
            self.current_day = day
            self.day_max_kw = 0.0

        # month rollover: if day is in a different month than current_day, reset daily dict
        if self.current_day and (day.month != self.current_day.month or day.year != self.current_day.year):
            self.daily_max_by_date = {}

        # day rollover: finalize yesterday (store its døgnmaks), then reset
        if self.current_day and day != self.current_day:
            # store yesterday's max
            self.daily_max_by_date[self._date_key(self.current_day)] = float(self.day_max_kw)
            self.current_day = day
            self.day_max_kw = 0.0

        # hour rollover: finalize previous hour average into day_max
        if self.current_hour and hour_start != self.current_hour.start:
            self.day_max_kw = max(self.day_max_kw, self.current_hour.avg_kw)
            self.current_hour = HourBucket(start=hour_start)

        # add current sample into current hour
        self.current_hour.add(max(0.0, float(kw)))

    def top3_avg_kw(self) -> float:
        """Average of top 3 daily maxima in this month (kW)."""
        values = list(self.daily_max_by_date.values())

        # include today's max so far (based on finalized hours + partial hour average)
        if self.current_day:
            today_max = self.day_max_kw
            if self.current_hour:
                today_max = max(today_max, self.current_hour.avg_kw)
            values.append(today_max)

        values = [v for v in values if v is not None]
        if not values:
            return 0.0

        values.sort(reverse=True)
        top3 = values[:3]
        return sum(top3) / len(top3)
