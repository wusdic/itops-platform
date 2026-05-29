import request from './request'

export function getLDAPConfigs(params) {
  return request({
    url: '/ldap/',
    method: 'get',
    params
  })
}

export function getLDAPConfig(id) {
  return request({
    url: `/ldap/${id}`,
    method: 'get'
  })
}

export function createLDAPConfig(data) {
  return request({
    url: '/ldap/',
    method: 'post',
    data
  })
}

export function updateLDAPConfig(id, data) {
  return request({
    url: `/ldap/${id}`,
    method: 'put',
    data
  })
}

export function deleteLDAPConfig(id) {
  return request({
    url: `/ldap/${id}`,
    method: 'delete'
  })
}

export function testLDAPConnection(data) {
  return request({
    url: '/ldap/test-connection',
    method: 'post',
    data
  })
}

export function testLDAPConfig(id) {
  return request({
    url: `/ldap/${id}/test`,
    method: 'post',
    data: {}
  })
}

export function syncLDAPUsers(id) {
  return request({
    url: `/ldap/${id}/sync`,
    method: 'post'
  })
}

export function getLDAPSyncLogs(id, params) {
  return request({
    url: `/ldap/${id}/sync-logs`,
    method: 'get',
    params
  })
}

export function previewLDAPUsers(params) {
  return request({
    url: '/ldap/users-preview',
    method: 'get',
    params
  })
}
