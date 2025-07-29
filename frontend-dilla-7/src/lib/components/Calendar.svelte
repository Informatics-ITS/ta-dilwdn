<script lang="ts">
  const monthNames = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
  const dayNames = ['Sen', 'Sel', 'Rab', 'Kam', 'Jum', 'Sab', 'Min']

  let currentDate = new Date()
  let selectedDate: Date | null = null

  function getDaysInMonth(year: number, month: number): number {
    return new Date(year, month + 1, 0).getDate()
  }

  function getCalendarDays(year: number, month: number) {
    const days: { day: number; muted: boolean; fullDate: Date }[] = []
    const firstDay = new Date(year, month, 1).getDay()
    const offset = (firstDay + 6) % 7

    const prevMonthDays = getDaysInMonth(year, month - 1)
    for (let i = offset - 1; i >= 0; i--) {
      const date = new Date(year, month - 1, prevMonthDays - i)
      days.push({ day: prevMonthDays - i, muted: true, fullDate: date })
    }

    const thisMonthDays = getDaysInMonth(year, month)
    for (let i = 1; i <= thisMonthDays; i++) {
      const date = new Date(year, month, i)
      days.push({ day: i, muted: false, fullDate: date })
    }

    while (days.length % 7 !== 0) {
      const date = new Date(year, month + 1, days.length + 1 - (offset + thisMonthDays))
      days.push({ day: date.getDate(), muted: true, fullDate: date })
    }

    return days
  }

  function previousMonth() {
    currentDate.setMonth(currentDate.getMonth() - 1)
    currentDate = new Date(currentDate)
  }

  function nextMonth() {
    currentDate.setMonth(currentDate.getMonth() + 1)
    currentDate = new Date(currentDate)
  }

  function isToday(date: Date): boolean {
    const today = new Date()
    return date.getDate() === today.getDate() && date.getMonth() === today.getMonth() && date.getFullYear() === today.getFullYear()
  }

  function selectDate(date: Date) {
    selectedDate = date
    console.log('Selected:', date.toDateString())
  }
</script>

<div class="rounded-3xl border p-4 text-gray-900 w-full">
  <h3 class="font-semibold mb-2">Kalender</h3>

  <div class="flex justify-between items-center mb-2 text-sm font-semibold border-b border-gray-400 py-1">
    <button on:click={previousMonth} class="px-2 py-1 hover:bg-white rounded">&lt;</button>
    <span>{monthNames[currentDate.getMonth()]} {currentDate.getFullYear()}</span>
    <button on:click={nextMonth} class="px-2 py-1 hover:bg-white rounded">&gt;</button>
  </div>

  <div class="grid grid-cols-7 text-center text-xs font-semibold text-primary mb-1">
    {#each dayNames as d}<div>{d}</div>{/each}
  </div>

  <div class="grid grid-cols-7 text-center text-sm ">
    {#each getCalendarDays(currentDate.getFullYear(), currentDate.getMonth()) as d}
      <button
        class={`w-8 h-8 rounded-full mx-auto transition 
          ${d.muted ? 'text-gray-400' : ''}
          ${isToday(d.fullDate) ? 'bg-white font-bold' : ''}
          ${selectedDate?.toDateString() === d.fullDate.toDateString() ? 'bg-primary text-white' : ''}
        `}
        on:click={() => selectDate(d.fullDate)}
      >
        {d.day}
      </button>
    {/each}
  </div>
</div>
