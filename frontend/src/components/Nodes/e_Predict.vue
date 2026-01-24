<template>
  <el-upload
    v-model:file-list="fileList"
    class="upload-demo border p-3 rounded-xl border-dashed bg-gray-50 max-w-75"
    action="api/upload"
    multiple
    :on-preview="handlePreview"
    :on-remove="handleRemove"
    :before-remove="beforeRemove"
    :limit="3"
    :on-exceed="handleExceed"
    :on-success="(msg:any)=>{
        props.data.value = msg
        }"
  >
    <el-button type="primary">Upload to Predict</el-button>
    <template #tip>
      <div class="el-upload__tip">
        jpg/png files with a size less than 500KB.
      </div>
    </template>
    <Handle
    type="source"
    :position="Position.Right"
    />
  </el-upload>

  
</template>

<script lang="ts" setup>
import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { UploadProps, UploadUserFile } from 'element-plus'
import type { NodeProps } from '@vue-flow/core';
import { Handle,Position } from '@vue-flow/core';

const emit = defineEmits(['response'])


const props = defineProps<NodeProps>()

const fileList = ref<UploadUserFile[]>()

const handleRemove: UploadProps['onRemove'] = (file, uploadFiles) => {
  console.log(file, uploadFiles)
}

const handlePreview: UploadProps['onPreview'] = (uploadFile) => {
  console.log(uploadFile)
}

const handleExceed: UploadProps['onExceed'] = (files, uploadFiles) => {
  ElMessage.warning(
    `The limit is 3, you selected ${files.length} files this time, add up to ${
      files.length + uploadFiles.length
    } totally`
  )
}

const beforeRemove: UploadProps['beforeRemove'] = (uploadFile, uploadFiles) => {
  return ElMessageBox.confirm(
    `Cancel the transfer of ${uploadFile.name} ?`
  ).then(
    () => true,
    () => false
  )
}


</script>

