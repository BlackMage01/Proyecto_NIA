document.getElementById('download-btn').addEventListener('click', function() {
    const month = document.getElementById('month-select').value;
    if (!month) {
        alert('Please select a month.');
        return;
    }

    const articles = [];
    document.querySelectorAll('ul li').forEach(li => {
        const link = li.querySelector('a').href;
        const title = li.querySelector('a').textContent;
        const dateSource = li.textContent.replace(title, '').trim();
        const [source, date] = dateSource.split('|').map(item => item.trim());

        // Parse the date to check if it matches the selected month
        const dateParts = date.split(',')[1].trim().split(' ');
        const articleMonth = dateParts[1]; // e.g., "Ene"

        // Map Spanish month abbreviations to numerical values
        const monthMap = {
            "Ene": "01", "Feb": "02", "Mar": "03", "Abr": "04", "May": "05", "Jun": "06",
            "Jul": "07", "Ago": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dic": "12"
        };

        if (monthMap[articleMonth] === month) {
            articles.push({
                Title: title,
                Link: link,
                Date: date,
                Source: source
            });
        }
    });

    if (articles.length === 0) {
        alert('No existen artículos para el mes elegido.')
        return;
    }

   const ws = XLSX.utils.json_to_sheet(articles);

    // Create a workbook
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Articles');

    // Download the Excel file
    XLSX.writeFile(wb, `articulos_mes_${month}.xlsx`);
});