(function () {
    const grid = document.getElementById('equipmentPhotoGrid');
    const input = document.getElementById('equipmentPhotoInput');

    if (!grid || !input) {
        return;
    }

    const addTile = grid.querySelector('[data-add-photo]');
    let selectedFiles = [];

    function updateInputFiles() {
        if (!window.DataTransfer) {
            return;
        }
        const transfer = new DataTransfer();
        selectedFiles.forEach(function (file) {
            transfer.items.add(file);
        });
        input.files = transfer.files;
    }

    function createPhotoTile(file) {
        const tile = document.createElement('div');
        tile.className = 'equipment-photo-tile';
        tile.setAttribute('data-photo-tile', '');
        tile.draggable = true;
        tile.file = file;

        const preview = document.createElement('img');
        preview.alt = file.name;
        preview.src = URL.createObjectURL(file);

        const actions = document.createElement('div');
        actions.className = 'equipment-photo-actions';

        const replaceButton = document.createElement('button');
        replaceButton.type = 'button';
        replaceButton.className = 'equipment-photo-action';
        replaceButton.textContent = 'Trocar foto';

        const replaceInput = document.createElement('input');
        replaceInput.type = 'file';
        replaceInput.accept = 'image/*';
        replaceInput.name = 'fotos';
        replaceInput.hidden = true;

        replaceButton.addEventListener('click', function () {
            replaceInput.click();
        });

        replaceInput.addEventListener('change', function () {
            const replacement = replaceInput.files[0];
            if (!replacement) {
                return;
            }
            const index = selectedFiles.indexOf(tile.file);
            if (index >= 0) {
                selectedFiles[index] = replacement;
            }
            tile.file = replacement;
            preview.src = URL.createObjectURL(replacement);
            preview.alt = replacement.name;
            updateInputFiles();
        });

        const removeButton = document.createElement('button');
        removeButton.type = 'button';
        removeButton.className = 'equipment-photo-action';
        removeButton.textContent = 'Excluir foto';
        removeButton.addEventListener('click', function () {
            URL.revokeObjectURL(preview.src);
            selectedFiles = selectedFiles.filter(function (file) {
                return file !== tile.file;
            });
            tile.remove();
            updateInputFiles();
        });

        actions.append(replaceButton, removeButton);
        tile.append(preview, actions, replaceInput);
        tile.addEventListener('dragstart', function (event) {
            tile.classList.add('is-dragging');
            event.dataTransfer.effectAllowed = 'move';
            event.dataTransfer.setData('text/plain', '');
        });
        tile.addEventListener('dragend', function () {
            tile.classList.remove('is-dragging');
            selectedFiles = Array.from(grid.querySelectorAll('[data-photo-tile]:not([data-add-photo])'))
                .map(function (photoTile) {
                    return photoTile.file;
                })
                .filter(Boolean);
            updateInputFiles();
        });
        return tile;
    }

    input.addEventListener('change', function () {
        Array.from(input.files).forEach(function (file) {
            selectedFiles.push(file);
            grid.insertBefore(createPhotoTile(file), addTile);
        });
        updateInputFiles();
    });

    grid.addEventListener('dragover', function (event) {
        event.preventDefault();
        const dragging = grid.querySelector('.is-dragging');
        const target = event.target.closest('[data-photo-tile]:not([data-add-photo])');
        if (dragging && target && target !== dragging) {
            const rect = target.getBoundingClientRect();
            const insertAfter = event.clientX > rect.left + rect.width / 2;
            grid.insertBefore(dragging, insertAfter ? target.nextSibling : target);
        }
    });
})();
