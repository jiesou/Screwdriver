<template>
  <a-typography-title>
    螺丝管理
  </a-typography-title>
  <a-flex>
    <div style="margin-right: 15px;">
      <ExcelImporter />
      <ScrewTable :screws="eventBus.movingStreamer.state.screws" />
      <ScrewCounter :num="eventBus.movingStreamer.state.screw_count" />
    </div>
    <ScrewMap :screws="eventBus.movingStreamer.state.screws" :position="eventBus.movingStreamer.state.position" style="z-index: -1"/>
  </a-flex>
</template>

<script setup>

import eventBus from '@/units/eventBus';

import ScrewTable from '@/components/ScrewTable.vue';
import ScrewCounter from '@/components/ScrewCounter.vue';
import ScrewMap from '@/components/ScrewMap.vue';
import ExcelImporter from '@/components/ExcelImporter.vue';

</script>
