<script setup lang="ts">
  import {ProcessedEvent} from "../ts/schedule_types.ts";
  import {computed, ComputedRef, onMounted, ref} from "vue";
  import moment from "moment/moment";

  const props = defineProps<{
    talk: ProcessedEvent
  }>()

  const now = ref(moment())
  const duration_seconds: number = props.talk.moment_duration.asSeconds()

  const percent_completed: ComputedRef<number> = computed(() => {
    if (props.talk.date_start.isAfter(now.value)) {
      return  0
    } else {
      return now.value.diff(props.talk.date_start, 's', true) / duration_seconds * 100
    }
  })

  function clock_tick() {
    now.value = moment()
  }
  let lastClockTick: number|undefined = undefined
  function animation_callback(timestamp: number) {
    // limit the clock tick to 10 FPS
    if (lastClockTick === undefined || (timestamp - lastClockTick) > 100) {
      clock_tick()
      lastClockTick = timestamp
    }
    window.requestAnimationFrame(animation_callback)
  }
  onMounted(() => {
    window.requestAnimationFrame(animation_callback)
  })
</script>

<template>
  <div class="mb-2 w-full grid grid-cols-schedule text-4xl gap-2">
    <div class="font-numbers font-semibold text-5xl">{{ props.talk.start }}</div>
    <div class="w-4" :style="{backgroundColor: props.talk.color}">&nbsp;</div>
    <div style="position: relative">
      <h2 class="font-bold text-5xl">{{ props.talk.title }}</h2>
      <p>In {{ props.talk.room }}
        <template v-if="props.talk.speakers.length > 0"> with {{ props.talk.speakers.join(', ') }}</template>
      </p>
       <div :style='{position: "absolute", left: "0", top: "0", width: "100%", backgroundColor: "var(--color-neutral)", color: "var(--color-dark)", clipPath: `rect(0 ${percent_completed}% 100% 0`}'>
      <h2 class="font-bold text-5xl">{{ props.talk.title }}</h2>
      <p>In {{ props.talk.room }}
        <template v-if="props.talk.speakers.length > 0"> with {{ talk.speakers.join(', ') }}</template>
      </p>
    </div>
    </div>
  </div>
</template>

<style scoped>

</style>