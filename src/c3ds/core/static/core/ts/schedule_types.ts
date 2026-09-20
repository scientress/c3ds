import {Event, RoomName} from "../../../../static/ts/c3voc.ts";
import {Moment, Duration} from "moment";

export interface ProcessedEvent extends Event {
  date_start: Moment
  date_end: Moment
  moment_duration: Duration
  color: string
  speakers: string[]
  is_break: false
}

export interface Break {
  is_break: true
  date_start: Moment
  date_end: Moment
  moment_duration: Duration
  room: RoomName
  guid: string
}
