import { ref, computed } from 'vue'
import { CONFIG } from '@/config/constants'

/**
 * 分页 composable
 * @param {Object} options - 配置选项
 * @param {Function} options.fetchData - 数据获取函数
 * @param {Object} options.defaultParams - 默认查询参数
 */
export function usePagination(options = {}) {
  const { fetchData, defaultParams = {} } = options

  // 分页状态
  const currentPage = ref(1)
  const pageSize = ref(CONFIG.DEFAULT_PAGE_SIZE)
  const total = ref(0)

  // 查询参数
  const queryParams = ref({ ...defaultParams })

  // 加载状态
  const loading = ref(false)
  const error = ref(null)

  // 数据
  const dataList = ref([])

  // 计算属性
  const totalPages = computed(() => Math.ceil(total.value / pageSize.value))
  const hasNextPage = computed(() => currentPage.value < totalPages.value)
  const hasPrevPage = computed(() => currentPage.value > 1)

  // 方法
  const loadData = async (params = {}) => {
    loading.value = true
    error.value = null
    try {
      const mergedParams = {
        page: currentPage.value,
        page_size: pageSize.value,
        ...queryParams.value,
        ...params
      }
      const result = await fetchData(mergedParams)
      
      if (result) {
        dataList.value = Array.isArray(result) ? result : (result.items || [])
        total.value = result.total || dataList.value.length
      }
      return result
    } catch (err) {
      error.value = err.message
      dataList.value = []
      throw err
    } finally {
      loading.value = false
    }
  }

  const setPage = (page) => {
    currentPage.value = page
    return loadData()
  }

  const setPageSize = (size) => {
    pageSize.value = size
    currentPage.value = 1
    return loadData()
  }

  const setQueryParams = (params) => {
    queryParams.value = { ...params }
    currentPage.value = 1
    return loadData()
  }

  const resetQuery = () => {
    queryParams.value = { ...defaultParams }
    currentPage.value = 1
  }

  const nextPage = () => {
    if (hasNextPage.value) {
      return setPage(currentPage.value + 1)
    }
  }

  const prevPage = () => {
    if (hasPrevPage.value) {
      return setPage(currentPage.value - 1)
    }
  }

  return {
    // 状态
    currentPage,
    pageSize,
    total,
    queryParams,
    loading,
    error,
    dataList,
    
    // 计算属性
    totalPages,
    hasNextPage,
    hasPrevPage,
    
    // 方法
    loadData,
    setPage,
    setPageSize,
    setQueryParams,
    resetQuery,
    nextPage,
    prevPage
  }
}
