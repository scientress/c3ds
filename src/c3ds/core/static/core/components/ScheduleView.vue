<script setup lang="ts">
import {Schedule} from "../../../../static/ts/c3voc.ts"
import {ProcessedEvent} from "../ts/schedule_types.ts";
import {computed, ComputedRef, onMounted, ref} from "vue"
  import moment from 'moment'
  import ScheduleRow from "./ScheduleRow.vue";

  interface Track {
    name?: string;
    color?: string;
    slug?: string;
  }

  const props = withDefaults(defineProps<{
    initialSchedule?: Schedule
    room_filter?: string[]
  }>(), {
    room_filter: () => []
  })

  const schedule = ref(props.initialSchedule)
  const now = ref(moment())

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

  const next_talks: ComputedRef<ProcessedEvent[]> = computed(() => {
    let max_talks = Math.floor(window.innerHeight / 96)
    if (schedule?.value === undefined) {
      console.log('schedule missing')
      return []
    }
    let _next_talks: ProcessedEvent[] = []
    daysLoop: for (let day of schedule.value.conference.days) {
      roomsLoop: for (let room in day.rooms) {
        for (let event of day.rooms[room]) {
          const talk = event as ProcessedEvent
          if (props.room_filter.length > 0 && !props.room_filter.includes(talk.room)) {
            continue
          }
          talk.date_start = moment(event.date)
          talk.date_end = talk.date_start.clone()
          talk.moment_duration = moment.duration(talk.duration)
          talk.date_end.add(talk.moment_duration)
          if (talk.date_end.isBefore(now.value)) continue
          talk.color = talk.track ? tracks.value[talk.track]?.color || '' : ''
          talk.speakers = talk.persons.map((person) => {
            return person.name || ''
          })
          _next_talks.push(talk)
          if (_next_talks.length >= max_talks) break
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
    return _next_talks
  })

  function minute_tick() {
    console.log("boop")
    now.value = moment()
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
    <ScheduleRow v-for="talk in next_talks" :key="talk.guid" :talk="talk"></ScheduleRow>
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