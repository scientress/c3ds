import {Event} from "../../../../static/ts/c3voc.ts";
import {Moment, Duration} from "moment";

export interface ProcessedEvent extends Event {
  date_start: Moment
  date_end: Moment
  moment_duration: Duration
  color: string
  speakers: string[]
}