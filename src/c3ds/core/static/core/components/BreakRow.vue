<script setup lang="ts">
import {Break} from "../ts/schedule_types.ts";
  import {computed, ComputedRef, onMounted, ref} from "vue";
  import {getCurrentTime} from "../ts/ntp.ts";

  const props = defineProps<{
    talk: Break
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
  <div class="mb-2 w-full text-4xl">
    <div :style="{background: `linear-gradient(90deg, var(--color-secondary-tint-03) ${percent_completed}%, rgba(0,0,0,0) ${percent_completed}%)`}" class="pl-2 pr-1 w-full justify-center">
      <div class="w-full py-1 flex items-center text-md before:flex-1 before:border-t before:border-neutral before:me-6 after:flex-1 after:border-t after:border-neutral after:ms-6">
        {{ props.talk.moment_duration.humanize() }} break in {{ props.talk.room }}
      </div>
    </div>
  </div>
</template>

<style scoped>

</style>
