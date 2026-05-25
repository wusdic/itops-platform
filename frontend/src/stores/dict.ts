import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import request from '../api/request'

export const useDictStore = defineStore('dict', () => {
  // 字典类型列表缓存
  const dictTypes = ref<any[]>([])
  // 字典项列表缓存 { [typeCode]: items[] }
  const dictItemsMap = ref<Record<string, any[]>>({})
  // 所有字典项缓存（用于 getDictLabel 快速查找）
  const allItemsMap = ref<Record<string, Record<string, string>>>({})
  // 加载状态
  const loading = ref(false)
  const itemsLoading = ref(false)

  // 判断是否已加载
  const isTypesLoaded = computed(() => dictTypes.value.length > 0)
  const isItemsLoaded = (typeCode: string) => computed(() => (dictItemsMap.value[typeCode]?.length ?? 0) > 0)

  /**
   * 获取字典类型列表
   */
  const fetchDictTypes = async () => {
    if (loading.value) return
    loading.value = true
    try {
      const res = await request.get('/admin/dict')
      dictTypes.value = res.items || res || []
    } catch (error) {
      console.error('Failed to fetch dict types:', error)
      dictTypes.value = []
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取所有字典项（用于快速查找标签）
   */
  const fetchAllItems = async () => {
    if (itemsLoading.value) return
    itemsLoading.value = true
    try {
      const res = await request.get('/admin/dict/all-items')
      const items = res.items || res || []
      // 按 type_code 分组，构建快速查找映射
      const grouped: Record<string, any[]> = {}
      const lookup: Record<string, Record<string, string>> = {}
      
      for (const item of items) {
        const typeCode = item.type_code || item.typeCode
        if (!grouped[typeCode]) {
          grouped[typeCode] = []
          lookup[typeCode] = {}
        }
        grouped[typeCode].push(item)
        // value 可以是 value 或 item.value
        const value = item.value ?? item.item?.value
        const label = item.label ?? item.item?.label
        if (value !== undefined && label !== undefined) {
          lookup[typeCode][String(value)] = label
        }
      }
      
      dictItemsMap.value = grouped
      allItemsMap.value = lookup
    } catch (error) {
      console.error('Failed to fetch all dict items:', error)
    } finally {
      itemsLoading.value = false
    }
  }

  /**
   * 根据类型编码获取字典项列表
   */
  const getDictItems = async (typeCode: string) => {
    // 如果缓存中有，直接返回
    if (dictItemsMap.value[typeCode]?.length) {
      return dictItemsMap.value[typeCode]
    }
    // 否则从 all-items 中获取（假设 all-items 已加载）
    if (Object.keys(allItemsMap.value).length > 0) {
      return allItemsMap.value[typeCode] 
        ? Object.entries(allItemsMap.value[typeCode]).map(([value, label]) => ({ type_code: typeCode, value, label }))
        : []
    }
    // 如果都没有，先获取 all-items
    await fetchAllItems()
    return dictItemsMap.value[typeCode] || []
  }

  /**
   * 根据类型编码和值获取标签
   */
  const getDictLabel = async (typeCode: string, value: any) => {
    // 确保 allItemsMap 已加载
    if (Object.keys(allItemsMap.value).length === 0) {
      await fetchAllItems()
    }
    const label = allItemsMap.value[typeCode]?.[String(value)]
    return label ?? String(value)
  }

  /**
   * 初始化字典数据（同时获取类型和所有项）
   */
  const initDict = async () => {
    await Promise.all([fetchDictTypes(), fetchAllItems()])
  }

  /**
   * 清除缓存
   */
  const clearDict = () => {
    dictTypes.value = []
    dictItemsMap.value = {}
    allItemsMap.value = {}
  }

  return {
    dictTypes,
    dictItemsMap,
    allItemsMap,
    loading,
    itemsLoading,
    isTypesLoaded,
    isItemsLoaded,
    fetchDictTypes,
    fetchAllItems,
    getDictItems,
    getDictLabel,
    initDict,
    clearDict
  }
})
