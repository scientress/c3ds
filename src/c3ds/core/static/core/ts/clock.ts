import moment from 'moment';

(() => {
  const container = document.getElementById('clock')
  if (container === null || container.dataset['dayZero'] === undefined) return
  const dayElement = container.querySelector('p span')
  const timeElement = container.querySelector('p:last-child')
  if (dayElement === null || timeElement === null) return;
  const dayZero = moment(container.dataset['dayZero'])

  const update_time = () => {
    const now = moment()
    const diff = moment.duration(now.diff(dayZero))
    dayElement.textContent = diff.days().toString()
    timeElement.textContent = now.format('HH:mm')
  }
  update_time()
  setInterval(update_time, 1000)
})()