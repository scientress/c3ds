import {ComponentPublicInstance, createApp} from 'vue'
import ScheduleView from "../components/ScheduleView.vue";
import axios from 'axios'
import {ScheduleJson, Schedule} from "../../../../static/ts/c3voc.ts";

declare const window: Window & typeof globalThis & {
 scheduleView?: ComponentPublicInstance<typeof ScheduleView>
}

const scheduleContainer: HTMLElement|null = document.querySelector('div.schedule-container')
if (scheduleContainer !== null) {
  let room_filter: string[] = (scheduleContainer.dataset['roomFilter'] || '')
    .split(';')
    .filter((value) => {return value !== ''})
  let schedule_url: string = (scheduleContainer.dataset['scheduleUrl'] || '')
  let current_schedule: Schedule|null = null
  const scheduleView: ComponentPublicInstance<typeof ScheduleView> = createApp(ScheduleView, {
    // initialSchedule: schedule.schedule
    room_filter
  }).mount('div.schedule-container')
  window.scheduleView = scheduleView

  const load_data = () => {
    console.log('fetching schedule')
    axios.get(schedule_url)
    .then((resp) => {
      const schedule: ScheduleJson = resp.data
      if (current_schedule === null || current_schedule.version !== schedule.schedule.version) {
        console.log("schedule version %s loaded", schedule.schedule.version)
        current_schedule = schedule.schedule
        scheduleView.schedule = current_schedule
      } else {
        console.log('schedule unchanged')
      }
    })
  }
  load_data()
  window.setInterval(load_data, 5*60*1000)
}
