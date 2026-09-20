<script setup lang="ts">
import {Room, Schedule} from "../../../../static/ts/c3voc.ts"
import {Break, ProcessedEvent} from "../ts/schedule_types.ts";
import {computed, ComputedRef, onMounted, ref} from "vue"
import moment from 'moment'
import ScheduleRow from "./ScheduleRow.vue";
import BreakRow from "./BreakRow.vue";
import {getCurrentTime} from "../ts/ntp.ts";
import {uuid} from "../ts/uuid.ts";

  interface Track {
    name?: string;
    color?: string;
    slug?: string;
  }

  const props = withDefaults(defineProps<{
    initialSchedule?: Schedule
    room_filter?: string[]
    guid_filter?: string[]
    duration_limit?: number
  }>(), {
    room_filter: () => [],
    guid_filter: () => [],
    duration_limit: undefined
  })

  const schedule = ref(props.initialSchedule)
  const now = ref(getCurrentTime())

  const tracks: ComputedRef<{[k: string]: Track}> = computed(() => {
    const tracks: {[k: string]: Track} = {}
    for (let track of schedule.value?.conference.tracks || []) {
      if (track.name) tracks[track.name] = track as Track
    }
    return tracks
  })

  // const rooms: ComputedRef<{[k: string]: Room}> = computed(() => {
  //   const rooms: {[k: string]: Room} = {}
  //   for (let room of schedule.value?.conference.rooms || []) {
  //     rooms[room.name] = room
  //   }
  //   return rooms
  // })

  const guid_rooms: ComputedRef<{[k: string]: Room}> = computed(() => {
    const guid_rooms: {[k: string]: Room} = {}
    for (let room of schedule.value?.conference.rooms || []) {
      if (room.guid) guid_rooms[room.guid] = room
    }
    return guid_rooms
  })

  const room_filter_combined: ComputedRef<string[]> = computed(() => {
    let guid_room_names: string[] = []
    if (props.guid_filter.length > 0) {
      for (let room_guid of props.guid_filter) {
        guid_room_names.push(guid_rooms.value[room_guid].name)
      }
    }
    if (props.room_filter.length > 0) {
      return guid_room_names.concat(props.room_filter)
    }
    return guid_room_names
  })

  const next_events: ComputedRef<(ProcessedEvent | Break)[]> = computed(() => {
    let max_talks = Math.floor(window.innerHeight / 96)
    if (schedule?.value === undefined) {
      console.log('schedule missing')
      return []
    }
    let _next_talks: (ProcessedEvent)[] = []
    daysLoop: for (let day of schedule.value.conference.days) {
      roomsLoop: for (let room in day.rooms) {
        for (let event of day.rooms[room]) {
          const talk = event as ProcessedEvent
          talk.is_break = false;
          if (room_filter_combined.value.length > 0 && !room_filter_combined.value.includes(talk.room)) {
            continue
          }
          talk.date_start = moment(event.date)
          talk.date_end = talk.date_start.clone()
          talk.moment_duration = moment.duration(talk.duration)
          if (props.duration_limit && talk.moment_duration.asMinutes() > props.duration_limit) continue
          talk.date_end.add(talk.moment_duration)
          if (talk.date_end.isBefore(now.value)) continue
          talk.color = talk.track ? tracks.value[talk.track]?.color || '' : ''
          talk.speakers = talk.persons.map((person) => {
            return person.name || person.public_name as string || ''
          })
          _next_talks.push(talk)
        }
      }
    }
    const priorityRooms = ['One', 'Ground', 'Zero', 'Fuse']
    _next_talks.sort((a, b) => {
      // sort by start time and date
      if (a.date_start.isBefore(b.date_start)) return -1
      if (a.date_start.isAfter(b.date_start)) return 1

      // if it is the same, sort by room name

      // forst check special rooms
      const aInPriorityRooms = priorityRooms.includes(a.room)
      const bInPriorityRooms = priorityRooms.includes(b.room)
      if (aInPriorityRooms || bInPriorityRooms) {
        if (!aInPriorityRooms) return 1
        if (!bInPriorityRooms) return -1
        return (priorityRooms.indexOf(a.room) < priorityRooms.indexOf(b.room)) ? -1: 1
      }

      // then sort alphabetical
      if (a.room < b.room) return -1
      if (a.room > b.room) return 1
      return 0
    })

    let _next_talks_with_breaks: (ProcessedEvent | Break)[] = []

    for (let talk_idx = 0; talk_idx < _next_talks.length; talk_idx++) {
      const talk = _next_talks[talk_idx]
      const room = talk.room
      const next_talk_in_room = _next_talks.find((_talk, _talk_idx) => {
        if (_talk_idx <= talk_idx) return false
        return _talk.room === room;
      });

      const next_talk_start = moment(next_talk_in_room?.date)

      const _break: Break = {
        room,
        date_start: talk.date_end,
        date_end: next_talk_start,
        moment_duration: moment.duration(next_talk_start.diff(talk.date_end)),
        guid: uuid(),
        is_break: true,
      }

      console.log('_break', _break)
      _next_talks_with_breaks.push(talk)

      if (_break.moment_duration.asSeconds() < 10) continue
      _next_talks_with_breaks.push(_break)
    }

    return _next_talks_with_breaks.slice(0, max_talks)
  })

  function minute_tick() {
    now.value = getCurrentTime()
    window.setTimeout(() => {
      minute_tick()
    }, (60 - now.value.second() - 1) * 1000 + 1000 - now.value.milliseconds())
  }
  onMounted(() => {
    console.log(`the component is now mounted.`)
    minute_tick()
  })

  defineExpose({
    schedule,
    now,
    minute_tick
  })
</script>

<template>
  <TransitionGroup name="list" tag="div" class="schedule flex flex-col flex-wrap overflow-hidden flex-grow text-neutral">
    <template v-for="event in next_events" :key="event.guid">
      <ScheduleRow v-if="!event.is_break" :talk="event"></ScheduleRow>
      <BreakRow v-if="event.is_break" :talk="event"></BreakRow>
    </template>
  </TransitionGroup>
  <div class="legend flex flex-wrap flex-shrink-0 -mx-1">
    <div v-for="track in tracks" :key="track.slug" class="track text-3xl mx-1" :style="{borderColor: track.color}">
      <p>{{ track.name }}</p>
<!--      <div class="legend-color" :style="{backgroundColor: track.color}"></div>-->
    </div>
  </div>
</template>

<style scoped>

</style>
