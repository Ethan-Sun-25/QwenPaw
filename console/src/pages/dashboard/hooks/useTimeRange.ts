import { useState, useCallback } from "react";
import dayjs from "dayjs";

export type RangeType = "today" | "7d" | "30d" | "custom";

export interface TimeRange {
  range: RangeType;
  start?: string;
  end?: string;
}

export function useTimeRange(defaultRange: RangeType = "7d") {
  const [timeRange, setTimeRange] = useState<TimeRange>({
    range: defaultRange,
  });

  const setRange = useCallback((range: RangeType) => {
    setTimeRange({ range });
  }, []);

  const setCustomRange = useCallback((start: string, end: string) => {
    setTimeRange({ range: "custom", start, end });
  }, []);

  const getQueryParams = useCallback(() => {
    const params: Record<string, string> = { range: timeRange.range };
    if (timeRange.range === "custom" && timeRange.start && timeRange.end) {
      params.start = timeRange.start;
      params.end = timeRange.end;
    }
    return params;
  }, [timeRange]);

  const rangeLabel = useCallback(() => {
    if (timeRange.range === "custom" && timeRange.start && timeRange.end) {
      return `${dayjs(timeRange.start).format("MM/DD")} - ${dayjs(timeRange.end).format("MM/DD")}`;
    }
    return timeRange.range;
  }, [timeRange]);

  return {
    timeRange,
    setRange,
    setCustomRange,
    getQueryParams,
    rangeLabel,
  };
}
