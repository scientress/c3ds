<script setup lang="ts">
import {onMounted, onUpdated, ref} from "vue";
import moment from "moment";
import {Moment} from "moment";
import {RemoteShellResult, RemoteShellCommand} from "../ts/remote_shell.ts";
import {WebSocketCommand} from "../ts/websocket.ts";

export interface LogEntry {
  id: number;
  timeSent: Moment,
  timeRecv: Moment | null,
  error: string | null,
  cmd: string;
  result: string | null;
}

const log = ref<HTMLDivElement | null>(null);

const props = withDefaults(defineProps<{
  initialLogEntries: LogEntry[],
}>(), {
  initialLogEntries: () => [],
});

const logEntries = ref(props.initialLogEntries);

class WebSocketBackend {
  ws: WebSocket | null = null

  displaySlug: string | null;

  input: HTMLInputElement | null = null;
  log: HTMLDivElement | null = null;

  lastId: number = 0;

  constructor(autoconnect: boolean) {
    this.displaySlug = document.querySelector('body')?.dataset['displaySlug'] || null
    this.input = document.querySelector('#cmd') || null;
    this.log = document.querySelector('#log') || null;

    this.input?.addEventListener('keydown', (e) => {
      if (!(e.key === 'Enter' || e.keyCode === 13) || this.input!.value === '') {
        return;
      }

      this.sendCmd(this.input!.value);
      this.input!.value = "";
    });

    if (autoconnect) this.connect()
  }


  connect() {
    if (this.displaySlug === undefined || this.displaySlug == null) {
      return
    }

    this.ws = new WebSocket(
        (window.location.protocol === 'https:' ? 'wss://' : 'ws://')
        + window.location.host
        + '/ws/shell/'
        + this.displaySlug
        + '/'
    )
    this.ws.onopen = () => {
      console.log('open');
    }
    this.ws.onmessage = (e) => {
      console.log("got data from websocket:", e.data)
      const data: WebSocketCommand = JSON.parse(e.data);
      switch (data?.cmd) {

        case 'rsRES':
          this.onRemoteShellResult(data as RemoteShellResult);
          break;

      }
    }
    this.ws.onclose = () => {
      this.reconnect()
    }
  }

  reconnect() {
    this.ws?.close()
    const timeout = 5000 + 2000 * Math.random()
    console.log('WS connection died, reconencting in %d', timeout)
    window.setTimeout(() => {
      this.connect()
    }, timeout)
  }

  onRemoteShellResult(cmd: RemoteShellResult) {
    if (!cmd.id) {
      return;
    }

    const l = this.getLogElement(cmd.id);
    if (!l) {
      return;
    }

    l.timeRecv = moment();
    l.error = cmd.error;
    l.result = cmd.result;
  }

  sendCmd(cmd: string) {
    if (this.displaySlug === undefined || this.displaySlug == null) {
      return;
    }

    this.lastId += 1;

    const wsCmd: RemoteShellCommand = {
      cmd: 'rsMSG',
      id: this.lastId,
      payload: cmd,
      displaySlug: this.displaySlug,
    };

    this.addLogElement(wsCmd);

    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws?.send(JSON.stringify(wsCmd));
    } else {
      const l = this.getLogElement(wsCmd.id!);
      if (!l) {
        return;
      }

      l.error = 'WebSocket.send failed';
      l.timeRecv = l.timeSent;
    }
  }

  addLogElement(cmd: RemoteShellCommand) {
    logEntries.value.push({
      id: cmd.id!,
      cmd: cmd.payload!,
      timeSent: moment(),
      timeRecv: null,
      error: null,
      result: null
    });


    // if (this.log?.scrollTop != this.log?.scrollHeight) {
    //
    // }
  }

  getLogElement(id: number) {
    return logEntries.value.find((v) => v.id === id);
  }
}


onUpdated(async () => {
  console.log(log);

  // await nextTick();
  log?.value?.scrollTo({behavior: 'instant', left: 0, top: log?.value!.scrollHeight - log?.value!.clientHeight});
});

onMounted(() => {
  new WebSocketBackend(true);
});


defineExpose({
  logEntries,
});
</script>

<template>
  <div class="shell">

    <div id="log" ref="log">
      <div class="entry" v-for="entry in logEntries" :class="{ok: entry.error === null && entry.result !== null, err: entry.error !== null}">
        <div class="sent">
          <p class="id">{{ entry.id }}</p>
          <p class="time">
            <span>{{ entry.timeSent.format("HH:mm:ss:SSS") }}</span>
            <span>{{ entry.timeRecv?.format("HH:mm:ss:SSS") || '-' }}</span>
          </p>
          <p class="cmdstr">{{ entry.cmd }}</p>
        </div>
        <div class="recv">
          <p v-if="entry.result !== null">{{ entry.result }}</p>
          <p v-if="entry.error !== null">{{ entry.error }}</p>
        </div>
      </div>
    </div>
    <input type="text" id="cmd"/>
  </div>

</template>

<style scoped>

</style>