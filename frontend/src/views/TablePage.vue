

<template>
    <div>
    <h3>Добавить адреса:</h3>
    <div v-for="(field, index) in newAddresses" :key="index" style="margin-bottom: 5px">
      <input
        type="text"
        v-model="field.value"
        :style="{ borderColor: isValidIP(field.value) || field.value === '' ? '#ccc' : 'red' }"
        placeholder="10.241.100.200"
        @input="onAddressInput(index)"
      />
    </div>
    <button @click="submitAddresses">Добавить</button>
  </div>
    <div>
        <button @click="pingAllAddresses">Обновить пинги всех адресов</button>


        <table border="1" cellpadding="5" cellspacing="0">
        <thead>
            <th @click="sortBy('id')">ID {{ sortField === 'id' ? (sortOrder === 'asc' ? '↑' : '↓') : '' }}</th>
            <th @click="sortBy('related_address')">Хост {{ sortField === 'related_address' ? (sortOrder === 'asc' ? '↑' : '↓') : '' }}</th>
            <th @click="sortBy('ping_time')">Ping, ms {{ sortField === 'ping_time' ? (sortOrder === 'asc' ? '↑' : '↓') : '' }}</th>
            <th @click="sortBy('delivered_packages_percentage')">% доставленных {{ sortField === 'delivered_packages_percentage' ? (sortOrder === 'asc' ? '↑' : '↓') : '' }}</th>
            <th>% недоставленных</th>
            <th @click="sortBy('last_successful_ping_timestamp')">Последний пинг {{ sortField === 'last_successful_ping_timestamp' ? (sortOrder === 'asc' ? '↑' : '↓') : '' }}</th>
        </thead>
        <tbody>
            <tr v-for="item in tableData" :key="item.id" :style="getRowStyle(item)">
            <td>{{ item.id }}</td>
            <td>{{ item.related_address }}</td>
            <td>{{ item.ping_time ?? 'null' }}</td>
            <td>{{ item.delivered_packages_percentage !== null ? item.delivered_packages_percentage + '%' : 'null'}}</td>
            <td>{{ item.delivered_packages_percentage !== null ? 100 - item.delivered_packages_percentage + '%': 'null' }}</td>
            <td>{{ new Date(item.last_successful_ping_timestamp).toLocaleString() }}</td>
            <td><button @click="deleteAddress(item.related_address)">Удалить адрес</button></td>
            </tr>
        </tbody>
      </table>
    </div>
    <button @click="downloadCsv">Скачать статистику</button>
    <div>
      <input type="file" accept=".csv" @change="handleFileUpload" />
      <button @click="uploadAddresses" :disabled="parsedAddresses.length === 0">Загрузить адреса</button>
    </div>
  </template>


<script setup>
import { ref, onMounted, computed } from 'vue'

const rawData = ref([])
const sortField = ref('id')
const sortOrder = ref('asc')
const parsedAddresses = ref([])

const tableData = computed(() => {
  if (!sortField.value) return rawData.value

  return [...rawData.value].sort((a, b) => {
    const valA = a[sortField.value]
    const valB = b[sortField.value]

    if (valA == null) return 1
    if (valB == null) return -1

    if (valA < valB) return sortOrder.value === 'asc' ? -1 : 1
    if (valA > valB) return sortOrder.value === 'asc' ? 1 : -1
    return 0
  })
})

const sortBy = (field) => {
  if (sortField.value === field) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortField.value = field
    sortOrder.value = 'asc'
  }
}

const newAddresses = ref([{ value: '' }])

function isValidIP(ip) {
  const regex =
    /^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$/
  return regex.test(ip)
}

function onAddressInput(index) {
  if (index === newAddresses.value.length - 1 && newAddresses.value[index].value !== '') {
    newAddresses.value.push({ value: '' })
  }
}

async function submitAddresses() {
  const validAddresses = newAddresses.value
    .map((addr) => addr.value.trim())
    .filter((addr) => isValidIP(addr))

  if (validAddresses.length === 0) {
    alert('Нет валидных адресов для добавления')
    return
  }

  try {
    const response = await fetch('http://localhost:8000/api/v1/addresses', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(validAddresses.map((value) => ({ value }))),
    })

    if (!response.ok) throw new Error('Ошибка при добавлении адресов')

    newAddresses.value = [{ value: '' }]
    await fetchData()
  } catch (err) {
    console.error(err)
  }
}



async function fetchData() {
  try {
    const response = await fetch('http://localhost:8000/api/v1/addresses')
    if (!response.ok) throw new Error('Ошибка загрузки данных')
    const data = await response.json()
    rawData.value = data
  } catch (err) {
    console.error(err)
  }
}
function getRowStyle(item) {
  if (
    item.ping_time === null ||
    item.delivered_packages_percentage === null

  ) {
    return {
      backgroundColor: 'lightcoral',
      color: 'white',
    }
  }
  return {
    backgroundColor: 'lightgreen',
    color: 'black',
  }
}

async function deleteAddress(address) {
  if (!confirm(`Удалить адрес ${address}?`)) return

  try {
    const response = await fetch(
      `http://localhost:8000/api/v1/addresses?address=${encodeURIComponent(address)}`,
      { method: 'DELETE' }
    )
    if (response.ok) {await fetchData()}
    if (!response.ok) throw new Error('Ошибка при удалении')
    tableData.value = tableData.value.filter((item) => item.related_address !== address)
  } catch (err) {
    console.error(err)
  }
}

const downloadCsv = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/v1/addresses/statistics');

    if (!response.ok) {throw new Error('Ошибка при получении CSV');}
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);

    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'statistics.csv');
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  } catch (err) {
    console.error('Ошибка при скачивании файла:', err);
  }
};


function handleFileUpload(event) {
  const file = event.target.files[0]
  if (!file) return

  const reader = new FileReader()
  reader.onload = (e) => {
    const lines = e.target.result.split(/\r?\n/)
    parsedAddresses.value = lines
      .map(line => line.trim())
      .filter(line => line.length > 0)
      .map(addr => ({ value: addr }))
  }
  reader.readAsText(file)
}

async function uploadAddresses() {
  try {
    const response = await fetch('http://localhost:8000/api/v1/addresses', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(parsedAddresses.value)
    })

    if (!response.ok) {
      const err = await response.text()
      throw new Error(`Ошибка: ${err}`)
    }

    alert('Загружено')
    parsedAddresses.value = []
  } catch (err) {
    console.error('Ошибка при загрузке адресов:', err)
    alert('Ошибка при загрузке адресов')
  }
}

async function pingAllAddresses() {
  try {
    const response = await fetch('http://localhost:8000/api/v1/addresses/ping_all')
    if (response.ok) {
      await fetchData()
    } else {
      console.error('Ошибка:', response.status)
    }
  } catch (err) {
    console.error('Ошибка:', err)
  }
}

onMounted(() => {
  fetchData()
})
</script>