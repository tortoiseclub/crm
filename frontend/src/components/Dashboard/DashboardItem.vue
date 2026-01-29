<template>
  <div class="h-full w-full">
    <div
      v-if="item.type == 'number_chart'"
      class="flex h-full w-full rounded shadow overflow-hidden"
      :class="item.data?.requiresFilter ? '' : 'cursor-pointer'"
    >
      <div
        v-if="item.data?.requiresFilter"
        class="h-full w-full flex flex-col items-center justify-center p-4 rounded-md bg-surface-white"
      >
        <div class="font-medium text-base mb-2">{{ item.data.title }}</div>
        <div class="text-sm text-ink-gray-5 text-center">{{ item.data.hint }}</div>
      </div>
      <Tooltip v-else-if="item.data" :text="__(item.data.tooltip)">
        <NumberChart
          class="!items-start"
          :key="index"
          :config="item.data"
        />
      </Tooltip>
    </div>
    <div
      v-else-if="item.type == 'spacer'"
      class="rounded bg-surface-white h-full overflow-hidden text-ink-gray-5 flex items-center justify-center"
      :class="editing ? 'border border-dashed border-outline-gray-2' : ''"
    >
      {{ editing ? __('Spacer') : '' }}
    </div>
    <div
      v-else-if="item.type == 'axis_chart'"
      class="h-full w-full rounded-md bg-surface-white shadow"
    >
      <div
        v-if="item.data?.requiresFilter"
        class="h-full flex flex-col items-center justify-center p-4"
      >
        <div class="font-medium text-base mb-2">{{ item.data.title }}</div>
        <div class="text-sm text-ink-gray-5 text-center">{{ item.data.hint }}</div>
      </div>
      <AxisChart v-else-if="item.data" :config="item.data" />
    </div>
    <div
      v-else-if="item.type == 'donut_chart'"
      class="h-full w-full rounded-md bg-surface-white shadow overflow-hidden"
    >
      <DonutChart v-if="item.data" :config="item.data" />
    </div>
    <div
      v-else-if="item.type == 'table_chart'"
      class="h-full w-full rounded-md bg-surface-white shadow overflow-auto flex flex-col"
    >
      <div
        v-if="item.data?.requiresFilter"
        class="h-full flex flex-col items-center justify-center p-4"
      >
        <div class="font-medium text-base mb-2">{{ item.data.title }}</div>
        <div class="text-sm text-ink-gray-5 text-center">{{ item.data.hint }}</div>
      </div>
      <div v-else-if="item.data" class="p-3 flex flex-col h-full">
        <div class="font-medium text-base mb-2">{{ item.data.title }}</div>
        <div v-if="item.data.subtitle" class="text-sm text-ink-gray-5 mb-2">
          {{ item.data.subtitle }}
        </div>
        <table class="w-full text-sm border-collapse">
          <thead>
            <tr class="border-b border-outline-gray-2">
              <th
                v-for="col in (item.data.columns || [])"
                :key="col.key"
                class="text-left py-2 px-2 font-medium"
              >
                {{ col.label }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(row, idx) in (item.data.data || [])"
              :key="idx"
              class="border-b border-outline-gray-1"
            >
              <td
                v-for="col in (item.data.columns || [])"
                :key="col.key"
                class="py-2 px-2"
              >
                {{ row[col.key] }}
              </td>
            </tr>
          </tbody>
        </table>
        <div
          v-if="!item.data.data?.length"
          class="flex-1 flex items-center justify-center text-ink-gray-5"
        >
          {{ __('No data') }}
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { AxisChart, DonutChart, NumberChart, Tooltip } from 'frappe-ui'

const props = defineProps({
  index: {
    type: Number,
    required: true,
  },
  item: {
    type: Object,
    required: true,
  },
  editing: {
    type: Boolean,
    default: false,
  },
})
</script>
