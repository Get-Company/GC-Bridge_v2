const app_sw6_backup = Vue.createApp({
    delimiters: ['${', '}'],
    methods: {
        async backup_sw6_db(event) {
            try {
                this.$showToast('success', 'DB Backup gestartet! Bitte beachte den Backup Pfad!');
                // Call the API endpoint
                const response = await fetch('/api/sw6/backup/db');
                const result = await response.json();
                console.log(result);
                // this.$showToast('success', result);
            } catch (error) {
                console.log(error);
                // handle the error as appropriate for your application
            } finally {
                // Remove spinner class from button
                event.target.classList.remove('spinner-grow');
            }
        },
        async backup_sw6_files(event) {
            try {
                this.$showToast('success', 'Files Backup gestartet! Bitte beachte den Backup Pfad!');
                // Call the API endpoint
                const response = await fetch('/api/sw6/backup/files');
                const result = await response.json();
                console.log(result);
                // this.$showToast('success', result);
            } catch (error) {
                console.log(error);
                // handle the error as appropriate for your application
            } finally {
                // Remove spinner class from button
                event.target.classList.remove('spinner-grow');
            }
        }
    }
})