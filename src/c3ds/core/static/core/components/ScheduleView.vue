<script setup lang="ts">
import {Schedule, Event} from "../../../../static/ts/c3voc.ts"
import {computed, ComputedRef, onMounted, ref} from "vue"
  import moment from 'moment'
  import {Moment} from "moment/moment";

  interface Talk extends Event {
    date_start: Moment
    date_end: Moment
    color: string
    speakers: string[]
    percent_completed: number
  }

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
  function clock_tick() {
    now.value = moment()
  }

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

  const next_talks: ComputedRef<Talk[]> = computed(() => {
    if (schedule?.value === undefined) {
      console.log('schedule missing')
      return []
    }
    let _next_talks: Talk[] = []
    for (let day of schedule.value.conference.days) {
      for (let room in day.rooms) {
        for (let event of day.rooms[room]) {
          const talk = event as Talk
          if (props.room_filter.length > 0 && !props.room_filter.includes(talk.room)) {
            continue
          }
          talk.date_start = moment(event.date)
          talk.date_end = talk.date_start.clone()
          let duration = moment.duration(talk.duration)
          talk.date_end.add(duration)
          if (talk.date_end.isBefore(now.value)) continue
          if (talk.date_start.isAfter(now.value)) {
            talk.percent_completed = 0
          } else {
            talk.percent_completed = now.value.diff(talk.date_start, 's') / duration.asSeconds() * 100
          }
          talk.color = talk.track ? tracks.value[talk.track]?.color || '' : ''
          talk.speakers = talk.persons.map((person) => {
            return person.name || ''
          })
          _next_talks.push(talk)
        }
      }
    }
    /*_next_talks.sort((a, b) => {
      // sort by start time and date
      if (a.date_start.isBefore(b.date_start)) return -1
      if (a.date_start.isAfter(b.date_start)) return 1

      // if it is the same, sort by room name
      if (a.room < b.room) return -1
      if (a.room > b.room) return 1
      return 0
    })*/
    return _next_talks
  })

  onMounted(() => {
    console.log(`the component is now mounted.`)
    window.setInterval(() => {
      clock_tick()
    }, 1000)
  })

  defineExpose({
    schedule,
    now,
    clock_tick
  })
</script>

<template>
  <div class="schedule flex flex-col flex-wrap overflow-hidden flex-grow text-secondary">
    <div v-for="talk in next_talks" :key="talk.guid" class="mb-2 w-full grid grid-cols-schedule text-4xl gap-2">
      <div class="font-numbers font-semibold text-5xl">{{ talk.start }}</div>
      <div class="w-4" :style="{backgroundColor: talk.color}">&nbsp;</div>
      <div :style='{background: `linear-gradient(90deg, #29114C ${talk.percent_completed}%, rgba(0,0,0,0) ${talk.percent_completed}%)`}'>
        <h2 class="font-bold text-5xl">{{ talk.title }}</h2>
        <p>{{ talk.room }}
          <template v-if="talk.speakers.length > 0"> with {{ talk.speakers.join(', ') }}</template>
        </p>
      </div>
    </div>
  </div>
  <div class="legend flex flex-wrap flex-shrink-0 -mx-1">
    <div v-for="track in tracks" :key="track.slug" class="track text-3xl mx-1" :style="{borderColor: track.color}">
      <p>{{ track.name }}</p>
<!--      <div class="legend-color" :style="{backgroundColor: track.color}"></div>-->
    </div>
  </div>
</template>

<style scoped>

</style>