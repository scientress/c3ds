<script setup lang="ts">
  import {ProcessedEvent} from "../ts/schedule_types.ts";
  import {computed, ComputedRef, onMounted, ref} from "vue";
  import {getCurrentTime} from "../ts/ntp.ts";

  const props = defineProps<{
    talk: ProcessedEvent
  }>()

  const now = ref(getCurrentTime())
  const duration_seconds: number = props.talk.moment_duration.asSeconds()

  const percent_completed: ComputedRef<number> = computed(() => {
    if (props.talk.date_start.isAfter(now.value)) {
      return  0
    } else {
      return now.value.diff(props.talk.date_start, 's', true) / duration_seconds * 100
    }
  })

  function clock_tick() {
    now.value = getCurrentTime()
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
    <div class="pr-1">
      <div class="font-numbers font-semibold text-5xl">{{ props.talk.start }}</div>
      <div class="font-numbers font-semibold text-2xl text-right text-gray-300">until {{ props.talk.date_end.format('HH:mm') }}</div>
    </div>
    <div class="w-4" :style="{backgroundColor: props.talk.color}">&nbsp;</div>
    <div :style="{background: `linear-gradient(90deg, var(--color-secondary-tint-03) ${percent_completed}%, rgba(0,0,0,0) ${percent_completed}%)`}" class="pl-2 pr-1">
      <h2 class="font-bold text-5xl">{{ props.talk.title }}</h2>
      <p>In {{ props.talk.room }}
        <template v-if="props.talk.speakers.length > 0"> with {{ props.talk.speakers.join(', ') }}</template>
      </p>
    </div>
  </div>
</template>

<style scoped>

</style>
