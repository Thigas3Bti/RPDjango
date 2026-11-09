(() => {
    const apiUrl = 'https://vbclnywgiwjuuuihaghk.supabase.co/rest/v1/stages';
    const apiKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZiY2xueXdnaXdqdXV1aWhhZ2hrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzIxOTA3OTgsImV4cCI6MjA4Nzc2Njc5OH0._FLS1C_tM3wbt962_69P2p507AnbuEsAbhy1EFU2P_Y';
    const allowedStatuses = new Set([
        'previsto',
        'inscricoes_em_breve',
        'inscricoes_abertas',
        'checkin_aberto',
        'em_andamento',
        'cancelado',
        'cancelada',
        'cancelled',
    ]);
    const activeStatuses = new Set(['checkin_aberto', 'em_andamento']);
    const cancelledStatuses = new Set(['cancelado', 'cancelada', 'cancelled']);
    const grid = document.getElementById('circuito-events-grid');
    const updated = document.getElementById('circuito-events-updated');

    if (!grid || !updated) return;

    let refreshing = false;
    let hasLoaded = false;

    function formatDate(dateString) {
        if (!dateString) return '';
        const [year, month, day] = dateString.split('-').map(Number);
        const date = new Date(year, month - 1, day);
        return new Intl.DateTimeFormat('pt-BR', {
            day: '2-digit',
            month: 'long',
            year: 'numeric',
        }).format(date);
    }

    function safeSlug(value) {
        return typeof value === 'string' && /^[a-z0-9-]+$/.test(value) ? value : '';
    }

    function addText(parent, tag, className, value) {
        const element = document.createElement(tag);
        if (className) element.className = className;
        element.textContent = value;
        parent.appendChild(element);
        return element;
    }

    function renderStage(stage) {
        const competition = stage.competitions || {};
        const competitionSlug = safeSlug(competition.slug);
        const stageSlug = safeSlug(stage.slug);
        const detailsUrl = competitionSlug && stageSlug
            ? `https://circuitorondonia.com.br/${competitionSlug}/${stageSlug}`
            : 'https://circuitorondonia.com.br/competicoes';
        const cancelled = cancelledStatuses.has(stage.status);
        const card = document.createElement('article');
        card.className = 'circuito-event-card';

        const imageUrl = stage.featured_image_url || stage.logo_url;
        if (typeof imageUrl === 'string' && imageUrl.startsWith('https://vbclnywgiwjuuuihaghk.supabase.co/')) {
            const image = document.createElement('img');
            image.className = 'circuito-event-image';
            image.src = imageUrl;
            image.alt = '';
            image.loading = 'lazy';
            card.appendChild(image);
        } else {
            const placeholder = document.createElement('div');
            placeholder.className = 'circuito-event-image-placeholder';
            placeholder.setAttribute('aria-hidden', 'true');
            placeholder.innerHTML = '<i class="bi bi-water"></i>';
            card.appendChild(placeholder);
        }

        const body = document.createElement('div');
        body.className = 'p-3';
        card.appendChild(body);

        if (competition.name) {
            addText(body, 'p', 'small text-muted mb-1', competition.name);
        }

        const status = addText(
            body,
            'span',
            `circuito-event-status${cancelled ? ' is-cancelled' : ''}`,
            cancelled
                ? 'Cancelado'
                : ({
                    previsto: 'Previsto',
                    inscricoes_em_breve: 'Inscrições em breve',
                    inscricoes_abertas: 'Inscrições abertas',
                    checkin_aberto: 'Check-in aberto',
                    em_andamento: 'Em andamento',
                }[stage.status] || stage.status),
        );
        status.setAttribute('aria-label', `Status: ${status.textContent}`);
        addText(body, 'h3', 'h5 fw-bold mt-2 mb-2', stage.name || 'Competição de pesca');

        const dateParts = [formatDate(stage.start_date)];
        if (stage.end_date && stage.end_date !== stage.start_date) {
            dateParts.push(formatDate(stage.end_date));
        }
        if (dateParts.some(Boolean)) {
            addText(body, 'p', 'small text-muted mb-1', dateParts.filter(Boolean).join(' – '));
        }
        const location = [stage.venue_name, stage.city].filter(Boolean).join(' · ');
        if (location) addText(body, 'p', 'small text-muted mb-3', location);

        const actions = document.createElement('div');
        actions.className = 'd-flex flex-wrap gap-2 mt-3';
        body.appendChild(actions);

        const details = document.createElement('a');
        details.className = 'btn btn-outline-success btn-sm';
        details.href = detailsUrl;
        details.target = '_blank';
        details.rel = 'noopener noreferrer';
        details.textContent = 'Ver competição';
        actions.appendChild(details);

        if (stage.status === 'inscricoes_abertas' && stageSlug) {
            const signup = document.createElement('a');
            signup.className = 'btn btn-success btn-sm';
            signup.href = `https://circuitorondonia.com.br/minha-area?regStage=${encodeURIComponent(stageSlug)}`;
            signup.target = '_blank';
            signup.rel = 'noopener noreferrer';
            signup.textContent = 'Inscrever-se';
            actions.appendChild(signup);
        }

        grid.appendChild(card);
    }

    async function refreshEvents() {
        if (refreshing) return;
        refreshing = true;

        try {
            const today = new Date();
            const date = [
                today.getFullYear(),
                String(today.getMonth() + 1).padStart(2, '0'),
                String(today.getDate()).padStart(2, '0'),
            ].join('-');
            const params = new URLSearchParams({
                select: '*,competitions(name,slug,logo_url,featured_image_url)',
                or: `(start_date.gte.${date},status.eq.em_andamento,status.eq.checkin_aberto)`,
                order: 'start_date.asc',
                limit: '100',
            });
            const response = await fetch(`${apiUrl}?${params}`, {
                headers: {
                    apikey: apiKey,
                    Authorization: `Bearer ${apiKey}`,
                },
            });
            if (!response.ok) throw new Error(`Circuit API returned ${response.status}`);

            const stages = await response.json();
            if (!Array.isArray(stages)) throw new Error('Invalid competition response');

            const availableStages = stages.filter((stage) => {
                const status = String(stage.status || '').toLowerCase();
                return allowedStatuses.has(status)
                    && (stage.start_date >= date || activeStatuses.has(status));
            });
            grid.replaceChildren();
            availableStages.forEach(renderStage);

            if (availableStages.length === 0) {
                addText(grid, 'div', 'dashboard-empty-state', 'Nenhuma competição disponível no momento.');
            }

            hasLoaded = true;
            updated.textContent = `Atualizado em ${new Intl.DateTimeFormat('pt-BR', {
                hour: '2-digit',
                minute: '2-digit',
            }).format(new Date())}. Verificamos novidades a cada minuto.`;
        } catch (error) {
            console.error('Não foi possível atualizar as competições do Circuito Rondônia.', error);
            updated.textContent = 'Não foi possível atualizar as competições agora. Consulte o site oficial pelo botão acima.';
            if (!hasLoaded) {
                grid.replaceChildren();
                addText(grid, 'div', 'dashboard-empty-state', 'A agenda oficial está indisponível no momento.');
            }
        } finally {
            refreshing = false;
        }
    }

    refreshEvents();
    window.setInterval(refreshEvents, 60 * 1000);
    window.addEventListener('focus', refreshEvents);
})();
