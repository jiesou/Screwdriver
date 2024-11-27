import { reactive } from 'vue';

const config = reactive({
    map_physics_width: 2,
    map_physics_height: 2,
    imu_vertical_h: 1,
    imu_center_point: [1, 1],
})
export default config;