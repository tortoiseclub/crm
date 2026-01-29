<template>
  <div class="flex flex-col gap-4">
    <div class="flex items-center justify-between gap-3">
      <div class="flex flex-col">
        <div class="text-base font-semibold text-ink-gray-9">
          {{ contextTitle }}
        </div>
        <div class="text-sm text-ink-gray-5">
          {{ contextDescription }}
        </div>
      </div>
      <div class="flex items-center gap-2">
        <div v-if="showTemplateSelector" class="hidden sm:flex items-center gap-2">
          <Select
            v-model="selectedTemplate"
            :options="templateOptions"
            class="w-56"
            :placeholder="__('Select a feedback form')"
          />
        </div>
        <Button
          :disabled="!hasLead"
          variant="solid"
          size="sm"
          :label="showTemplateSelector ? __('Create') : __('New feedback')"
          iconLeft="plus"
          :tooltip="!hasLead ? noLeadMessage : undefined"
          @click="showTemplateSelector ? createFeedbackFromTemplate() : openTemplateSelector()"
        />
      </div>
    </div>

    <div
      v-if="showTemplateSelector"
      class="sm:hidden mt-2 flex flex-col gap-2"
    >
      <Select
        v-model="selectedTemplate"
        :options="templateOptions"
        :placeholder="__('Select a feedback form')"
      />
      <div class="flex justify-end gap-2">
        <Button
          size="sm"
          variant="subtle"
          :label="__('Cancel')"
          @click="cancelTemplateSelector"
        />
        <Button
          size="sm"
          variant="solid"
          :label="__('Create')"
          iconLeft="plus"
          @click="createFeedbackFromTemplate()"
        />
      </div>
    </div>

    <div v-if="hasLead">
      <div class="border rounded-lg border-outline-gray-2 overflow-hidden">
        <div class="bg-surface-gray-1 px-3 py-2 text-xs font-medium text-ink-gray-6">
          {{ __('Previous feedback') }}
        </div>
        <div v-if="summary.loading" class="flex items-center justify-center py-6 gap-2">
          <LoadingIndicator class="h-4 w-4" />
          <span class="text-sm text-ink-gray-5">
            {{ __('Loading...') }}
          </span>
        </div>
        <div v-else-if="!summary.data?.length" class="py-6 text-center text-sm text-ink-gray-5">
          {{ __('No feedback recorded for this lead yet.') }}
        </div>
        <div
          v-else
          class="divide-y divide-outline-gray-2"
        >
          <button
            v-for="item in summary.data"
            :key="item.name"
            type="button"
            class="w-full px-3 py-2.5 flex items-center gap-3 text-left hover:bg-surface-gray-1 transition-colors"
            :class="{
              'bg-surface-blue-1': activeFeedback && activeFeedback.name === item.name,
            }"
            @click="selectExistingFeedback(item.name)"
          >
            <div class="flex flex-col flex-1 min-w-0">
              <div class="flex items-center gap-2">
                <span class="truncate font-medium text-sm text-ink-gray-9">
                  {{ item.feedback_form_label || item.feedback_form || item.name }}
                </span>
                <Badge
                  size="sm"
                  variant="subtle"
                  :theme="item.status === 'Submitted' ? 'green' : 'orange'"
                  :label="__(item.status)"
                />
              </div>
              <div class="flex items-center gap-2 mt-0.5 text-xs text-ink-gray-5">
                <span v-if="item.submitted_on">
                  {{ __('Submitted on') }} {{ formatDate(item.submitted_on) }}
                </span>
                <span v-if="item.submitted_by">
                  &middot;
                  {{ __('by') }}
                  {{ item.submitted_by }}
                </span>
              </div>
            </div>
            <div class="flex items-center gap-1">
              <Button
                v-if="item.status === 'Draft'"
                variant="ghost"
                size="sm"
                icon="trash-2"
                theme="red"
                :tooltip="__('Discard draft')"
                @click.stop="discardFeedback(item.name)"
              />
              <Button
                v-if="item.external_token"
                variant="ghost"
                size="sm"
                icon="external-link"
                :tooltip="__('Open external form')"
                @click.stop="openExternalForm(item.external_token)"
              />
            </div>
          </button>
        </div>
      </div>

      <div class="border rounded-lg border-outline-gray-2 overflow-hidden">
        <div class="bg-surface-gray-1 px-3 py-2 text-xs font-medium text-ink-gray-6">
          {{ activeFeedback ? __('Feedback form') : __('Select or create a feedback to start') }}
        </div>

        <div v-if="detailLoading" class="flex items-center justify-center py-8 gap-2">
          <LoadingIndicator class="h-4 w-4" />
          <span class="text-sm text-ink-gray-5">
            {{ __('Loading form...') }}
          </span>
        </div>

        <div v-else-if="!activeFeedback" class="py-8 text-center text-sm text-ink-gray-5">
          {{ __('Choose a feedback from the list above or create a new one.') }}
        </div>

        <form
          v-else
          class="flex flex-col gap-4 px-4 py-4"
          @submit.prevent="submitFeedback(true)"
        >
          <div
            v-for="question in questions"
            :key="question.rowname"
            class="flex flex-col gap-1"
          >
            <label class="flex items-center gap-1 text-sm font-medium text-ink-gray-9">
              <span>{{ question.label }}</span>
              <span v-if="question.is_mandatory" class="text-ink-red-5">*</span>
            </label>
            <p class="text-xs text-ink-gray-5">
              <span v-if="question.type === 'Select'">
                {{ __('Select one of the options') }}
              </span>
              <span v-else>
                {{ __('Type your answer') }}
              </span>
            </p>

            <Select
              v-if="question.type === 'Select'"
              v-model="question.value"
              :options="question.options"
              class="mt-1"
              :placeholder="__('Choose an option')"
            />
            <textarea
              v-else
              v-model="question.value"
              rows="3"
              class="mt-1 block w-full rounded border border-outline-gray-3 bg-surface-white px-2.5 py-1.5 text-sm text-ink-gray-9 outline-none focus:ring-2 focus:ring-ink-blue-4"
              :placeholder="__('Enter your answer')"
            />
          </div>

          <div class="flex items-center justify-between gap-2 pt-2 border-t border-outline-gray-2">
            <Button
              v-if="activeFeedback && activeFeedback.status === 'Draft'"
              type="button"
              variant="subtle"
              size="sm"
              theme="red"
              icon="trash-2"
              :label="__('Discard')"
              :loading="discarding"
              @click="discardActiveFeedback"
            />
            <div class="flex items-center gap-2 ml-auto">
              <Button
                type="button"
                variant="subtle"
                size="sm"
                :label="__('Save draft')"
                :loading="saving && !submitFlag"
                @click="submitFeedback(false)"
              />
              <Button
                type="submit"
                variant="solid"
                size="sm"
                :label="__('Submit')"
                :loading="saving && submitFlag"
              />
            </div>
          </div>
        </form>
      </div>
    </div>

    <div v-else class="border rounded-lg border-outline-gray-2 overflow-hidden">
      <div class="bg-surface-gray-1 px-3 py-2 text-xs font-medium text-ink-gray-6">
        {{ __('Feedback unavailable') }}
      </div>
      <div class="flex items-center justify-center p-6 text-sm text-ink-gray-5">
        {{ noLeadMessage }}
      </div>
    </div>
  </div>
</template>

<script setup>
import LoadingIndicator from '@/components/Icons/LoadingIndicator.vue'
import { Button, Badge, Select, createResource, toast } from 'frappe-ui'
import { ref, computed, watch } from 'vue'

const props = defineProps({
  lead: {
    type: String,
    default: '',
  },
  context: {
    type: String,
    default: 'lead',
  },
})

const summary = createResource({
  url: 'crm.fcrm.doctype.lead_feedback.api.get_feedback_summary',
  params: { lead: props.lead },
  auto: false,
})

if (props.lead) {
  summary.fetch({ lead: props.lead })
}

const templates = createResource({
  url: 'crm.fcrm.doctype.lead_feedback.api.get_feedback_templates',
  auto: true,
})

const activeFeedback = ref(null)
const questions = ref([])
const detailLoading = ref(false)
const saving = ref(false)
const submitFlag = ref(false)
const discarding = ref(false)

const hasTemplates = computed(() => templates.data && templates.data.length)

const hasLead = computed(() => !!props.lead)
const contextTitle = computed(() =>
  props.context === 'deal'
    ? __('Feedback (from linked lead)')
    : __('Lead feedback'),
)
const contextDescription = computed(() =>
  props.context === 'deal'
    ? __('Create and submit feedback for the lead linked to this deal')
    : __('Create and submit feedback for this lead'),
)
const noLeadMessage = computed(() =>
  props.context === 'deal'
    ? __('This deal does not have a linked lead yet. Please select a lead before recording feedback.')
    : __('Lead information is missing. Feedback cannot be recorded.'),
)

const showTemplateSelector = ref(false)
const selectedTemplate = ref('')

const templateOptions = computed(() =>
  (templates.data || []).map((t) => ({
    label: t.label || t.name,
    value: t.name,
  })),
)

watch(
  () => props.lead,
  (lead) => {
    if (lead) {
      summary.fetch({ params: { lead } })
      if (!selectedTemplate.value && templateOptions.value.length) {
        selectedTemplate.value = templateOptions.value[0].value
      }
    } else {
      summary.data = []
      showTemplateSelector.value = false
      selectedTemplate.value = ''
    }
  },
)

function formatDate(value) {
  if (!value) return ''
  try {
    return frappe.format(value, { fieldtype: 'Datetime' })
  } catch (e) {
    return value
  }
}

function openExternalForm(token) {
  if (!token) return
  const url = `/crm/lead_feedback?token=${encodeURIComponent(token)}`
  window.open(url, '_blank')
}

async function loadDetail(name) {
  if (!name) return
  detailLoading.value = true
  try {
    const data = await createResource({
      url: 'crm.fcrm.doctype.lead_feedback.api.get_feedback_detail',
      params: { name },
      auto: true,
    }).promise

    activeFeedback.value = data.feedback
    questions.value = (data.responses || []).map((q) => ({
      ...q,
      value: q.value || '',
    }))
  } catch (e) {
    console.error(e)
    toast.error(e.messages?.[0] || __('Failed to load feedback'))
  } finally {
    detailLoading.value = false
  }
}

function selectExistingFeedback(name) {
  loadDetail(name)
}

function openTemplateSelector() {
  if (!hasLead.value) {
    toast.error(noLeadMessage.value)
    return
  }

  if (!hasTemplates.value) {
    toast.error(__('No Feedback Form templates available'))
    return
  }

  showTemplateSelector.value = true

  if (!selectedTemplate.value && templateOptions.value.length) {
    selectedTemplate.value = templateOptions.value[0].value
  }
}

function cancelTemplateSelector() {
  showTemplateSelector.value = false
  selectedTemplate.value = ''
}

async function createFeedbackFromTemplate() {
  if (!hasLead.value) {
    toast.error(noLeadMessage.value)
    return
  }

  if (!hasTemplates.value) {
    toast.error(__('No Feedback Form templates available'))
    return
  }

  const template =
    (templates.data || []).find((t) => t.name === selectedTemplate.value) ||
    (templates.data || [])[0]
  if (!template) {
    toast.error(__('Please select a feedback form'))
    return
  }

  saving.value = true
  submitFlag.value = false
  try {
    const data = await createResource({
      url: 'crm.fcrm.doctype.lead_feedback.api.create_lead_feedback',
      params: {
        lead: props.lead,
        feedback_form: template.name,
      },
      auto: true,
    }).promise

    activeFeedback.value = data.feedback
    questions.value = (data.responses || []).map((q) => ({
      ...q,
      value: q.value || '',
    }))
    summary.reload()
    toast.success(__('Feedback created'))
  } catch (e) {
    console.error(e)
    toast.error(e.messages?.[0] || __('Failed to create feedback'))
  } finally {
    saving.value = false
  }
}

async function submitFeedback(submit) {
  if (!activeFeedback.value) return

  submitFlag.value = !!submit
  saving.value = true

  const payload = questions.value.map((q) => ({
    rowname: q.rowname,
    value: q.value,
  }))

  try {
    const data = await createResource({
      url: 'crm.fcrm.doctype.lead_feedback.api.update_feedback_responses',
      params: {
        name: activeFeedback.value.name,
        responses: payload,
        submit: submit ? 1 : 0,
      },
      auto: true,
    }).promise

    activeFeedback.value = data.feedback
    questions.value = (data.responses || []).map((q) => ({
      ...q,
      value: q.value || '',
    }))
    summary.reload()

    if (submit) {
      toast.success(__('Feedback submitted'))
    } else {
      toast.success(__('Draft saved'))
    }
  } catch (e) {
    console.error(e)
    toast.error(e.messages?.[0] || __('Failed to save feedback'))
  } finally {
    saving.value = false
  }
}

async function discardFeedback(name) {
  if (!name) return

  if (
    !confirm(
      __(
        'Are you sure you want to discard this draft feedback? This action cannot be undone.',
      ),
    )
  ) {
    return
  }

  discarding.value = true
  try {
    await createResource({
      url: 'crm.fcrm.doctype.lead_feedback.api.discard_feedback',
      params: { name },
      auto: true,
    }).promise

    summary.reload()

    // If the discarded feedback was active, clear it
    if (activeFeedback.value && activeFeedback.value.name === name) {
      activeFeedback.value = null
      questions.value = []
    }

    toast.success(__('Draft feedback discarded'))
  } catch (e) {
    console.error(e)
    toast.error(e.messages?.[0] || __('Failed to discard feedback'))
  } finally {
    discarding.value = false
  }
}

async function discardActiveFeedback() {
  if (!activeFeedback.value) return
  await discardFeedback(activeFeedback.value.name)
}
</script>

