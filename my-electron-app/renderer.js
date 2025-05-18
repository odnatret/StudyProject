let stockData = [];
let autoRefreshInterval;
let currentFilePath = null;
let audioNotification = new Audio('./alert.mp3');

document.getElementById('load-csv').addEventListener('click', async () => {
  try {
    const result = await window.electronAPI.openCSVDialog();
    
    if (!result.canceled && result.filePaths.length > 0) {
      currentFilePath = result.filePaths[0];
      loadCSV(currentFilePath);
    }
  } catch (error) {
    console.error('Ошибка при открытии диалога:', error);
    alert('Не удалось открыть диалоговое окно');
  }
});

// ... (остальные обработчики событий остаются без изменений)

async function loadCSV(filePath) {
  try {
    const csvData = await window.electronAPI.readCSVFile(filePath);
    
    const cleanData = csvData.replace(/^\uFEFF/, '');
    
    Papa.parse(cleanData, {
      header: true,
      skipEmptyLines: true,
      complete: (results) => {
        if (results.errors.length > 0) {
          console.error('Ошибки при парсинге CSV:', results.errors);
          alert(`Ошибка при обработке CSV файла: ${results.errors[0].message}`);
          return;
        }

        const requiredColumns = ['Время', 'Наименование', 'Кол-во', 'Ед. измерения', 'Место хранения'];
        const firstRow = results.data[0] || {};
        
        const missingColumns = requiredColumns.filter(col => !(col in firstRow));
        if (missingColumns.length > 0) {
          alert(`В файле отсутствуют обязательные столбцы: ${missingColumns.join(', ')}`);
          return;
        }

        stockData = results.data.filter(row => 
          row['Наименование'] && row['Кол-во'] && row['Место хранения']
        );
        
        updateTable(stockData);
        updateLastUpdateTime();
        checkZeroQuantityItems();
      },
      error: (error) => {
        console.error('Ошибка парсинга:', error);
        alert(`Ошибка при обработке CSV файла: ${error.message}`);
      }
    });
  } catch (error) {
    console.error('Ошибка чтения файла:', error);
    alert(`Ошибка при чтении файла: ${error.message}`);
  }
}

function updateTable(data) {
  const tableBody = document.querySelector('#stock-table tbody');
  tableBody.innerHTML = '';

  data.forEach(item => {
    const row = document.createElement('tr');
    const quantity = parseInt(item['Кол-во']) || 0;
    
    // Добавляем класс если товара нет в наличии
    if (quantity <= 0) {
      row.classList.add('out-of-stock');
    }
    
    const timeCell = document.createElement('td');
    timeCell.textContent = item['Время'] || '';
    row.appendChild(timeCell);
    
    const nameCell = document.createElement('td');
    nameCell.textContent = item['Наименование'] || '';
    row.appendChild(nameCell);
    
    const quantityCell = document.createElement('td');
    quantityCell.textContent = quantity;
    row.appendChild(quantityCell);
    
    const unitCell = document.createElement('td');
    unitCell.textContent = item['Ед. измерения'] || '';
    row.appendChild(unitCell);
    
    const locationCell = document.createElement('td');
    locationCell.textContent = item['Место хранения'] || '';
    row.appendChild(locationCell);
    
    tableBody.appendChild(row);
  });
}

function checkZeroQuantityItems() {
  const zeroItems = stockData.filter(item => {
    const quantity = parseInt(item['Кол-во']) || 0;
    return quantity <= 0;
  });

  if (zeroItems.length > 0) {
    // Воспроизводим звуковое уведомление
    audioNotification.play().catch(e => console.error('Ошибка воспроизведения звука:', e));
    
    // Можно добавить дополнительное уведомление
    const itemNames = zeroItems.map(item => item['Наименование']).join(', ');
    console.log(`Товары закончились: ${itemNames}`);
  }
}

function updateLastUpdateTime() {
  const now = new Date();
  const timeString = now.toLocaleTimeString();
  document.getElementById('last-update').textContent = timeString;
}

// Автообновление каждые 30 секунд
function startAutoRefresh() {
  if (autoRefreshInterval) {
    clearInterval(autoRefreshInterval);
  }
  
  autoRefreshInterval = setInterval(() => {
    if (currentFilePath) {
      loadCSV(currentFilePath);
    }
  }, 10000);
}

// Инициализация
startAutoRefresh();