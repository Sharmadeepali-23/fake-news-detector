document.addEventListener('DOMContentLoaded', () => {
    // =========================================================================
    // 1. Dark / Light Theme Switcher
    // =========================================================================
    const themeToggleBtn = document.getElementById('themeToggle');
    const htmlEl = document.documentElement;

    const savedTheme = localStorage.getItem('verinews_theme') || 'dark';
    htmlEl.setAttribute('data-theme', savedTheme);

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            const currentTheme = htmlEl.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            htmlEl.setAttribute('data-theme', newTheme);
            localStorage.setItem('verinews_theme', newTheme);
        });
    }

    // =========================================================================
    // 2. Mobile Menu Toggle
    // =========================================================================
    const mobileToggle = document.getElementById('mobileToggle');
    const navMenu = document.getElementById('navMenu');

    if (mobileToggle && navMenu) {
        mobileToggle.addEventListener('click', () => {
            navMenu.classList.toggle('active');
        });
    }

    // =========================================================================
    // 3. Typing Effect Animation (Home Hero Section)
    // =========================================================================
    const typingElement = document.getElementById('typingEffect');
    if (typingElement) {
        const phrases = [
            "Detecting misinformation with statistical precision...",
            "Verifying article credibility using Machine Learning...",
            "Exposing fake news using TF-IDF & Scikit-Learn classifiers..."
        ];
        let phraseIdx = 0;
        let charIdx = 0;
        let isDeleting = false;

        function typeLoop() {
            const currentPhrase = phrases[phraseIdx];
            if (isDeleting) {
                typingElement.textContent = currentPhrase.substring(0, charIdx - 1);
                charIdx--;
            } else {
                typingElement.textContent = currentPhrase.substring(0, charIdx + 1);
                charIdx++;
            }

            let typeSpeed = isDeleting ? 40 : 80;

            if (!isDeleting && charIdx === currentPhrase.length) {
                typeSpeed = 2000;
                isDeleting = true;
            } else if (isDeleting && charIdx === 0) {
                isDeleting = false;
                phraseIdx = (phraseIdx + 1) % phrases.length;
                typeSpeed = 500;
            }

            setTimeout(typeLoop, typeSpeed);
        }

        typeLoop();
    }

    // =========================================================================
    // 4. Detector Page Controls (Form, Character Counter, Samples, AJAX)
    // =========================================================================
    const detectorForm = document.getElementById('detectorForm');
    const contentInput = document.getElementById('contentInput');
    const headlineInput = document.getElementById('headlineInput');
    const charCounter = document.getElementById('charCounter');
    const btnClear = document.getElementById('btnClear');
    const btnSampleReal = document.getElementById('btnSampleReal');
    const btnSampleFake = document.getElementById('btnSampleFake');

    const loadingState = document.getElementById('loadingState');
    const emptyState = document.getElementById('emptyState');
    const resultCard = document.getElementById('resultCard');

    // Character Counter
    if (contentInput && charCounter) {
        const updateCount = () => {
            const len = contentInput.value.length;
            charCounter.textContent = `${len} character${len !== 1 ? 's' : ''}`;
        };
        contentInput.addEventListener('input', updateCount);
        updateCount();
    }

    // Clear Button
    if (btnClear && contentInput) {
        btnClear.addEventListener('click', () => {
            if (headlineInput) headlineInput.value = '';
            contentInput.value = '';
            if (charCounter) charCounter.textContent = '0 characters';
            if (resultCard) resultCard.classList.add('hidden');
            if (emptyState) emptyState.classList.remove('hidden');
        });
    }

    // Sample Preset Loader Helper
    const loadSampleNews = (type) => {
        fetch(`/api/sample-news?type=${type}`)
            .then(res => res.json())
            .then(data => {
                if (headlineInput) headlineInput.value = data.title;
                if (contentInput) {
                    contentInput.value = data.content;
                    contentInput.dispatchEvent(new Event('input'));
                }
            })
            .catch(err => console.error('Error fetching sample:', err));
    };

    if (btnSampleReal) btnSampleReal.addEventListener('click', () => loadSampleNews('real'));
    if (btnSampleFake) btnSampleFake.addEventListener('click', () => loadSampleNews('fake'));

    // AJAX Form Submission for Detector Page
    if (detectorForm) {
        detectorForm.addEventListener('submit', function (e) {
            // Check if AJAX can handle submit
            if (!contentInput || !contentInput.value.trim()) return;

            e.preventDefault();

            // UI Loading state
            if (emptyState) emptyState.classList.add('hidden');
            if (resultCard) resultCard.classList.add('hidden');
            if (loadingState) loadingState.classList.remove('hidden');

            const formData = new FormData(detectorForm);
            const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';

            fetch('/detect', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrfToken
                }
            })
            .then(response => response.json())
            .then(data => {
                if (loadingState) loadingState.classList.add('hidden');

                if (data.success && data.result) {
                    renderPredictionResult(data.result);
                } else {
                    alert(data.error || 'Failed to analyze article.');
                    if (emptyState) emptyState.classList.remove('hidden');
                }
            })
            .catch(err => {
                console.error('Detection request failed:', err);
                if (loadingState) loadingState.classList.add('hidden');
                if (emptyState) emptyState.classList.remove('hidden');
                alert('An error occurred during communication with the server.');
            });
        });
    }

    // Render Prediction Result Dynamically
    function renderPredictionResult(res) {
        if (!resultCard) return;

        const resultBadge = document.getElementById('resultBadge');
        const confidenceValue = document.getElementById('confidenceValue');
        const progressFill = document.getElementById('progressFill');
        const metaWords = document.getElementById('metaWords');
        const metaReadTime = document.getElementById('metaReadTime');
        const metaModel = document.getElementById('metaModel');
        const tagsCloud = document.getElementById('tagsCloud');
        const pdfReportLink = document.getElementById('pdfReportLink');

        if (resultBadge) {
            resultBadge.className = `result-badge ${res.is_real ? 'badge-real' : 'badge-fake'}`;
            resultBadge.innerHTML = res.is_real 
                ? `<i class="fa-solid fa-circle-check"></i> REAL NEWS ✅` 
                : `<i class="fa-solid fa-circle-xmark"></i> FAKE NEWS ❌`;
        }

        if (confidenceValue) confidenceValue.textContent = `${res.confidence}%`;

        if (progressFill) {
            progressFill.className = `progress-bar-fill ${res.is_real ? 'fill-real' : 'fill-fake'}`;
            progressFill.style.width = `${res.confidence}%`;
        }

        if (metaWords) metaWords.textContent = `${res.metadata.word_count} words`;
        if (metaReadTime) metaReadTime.textContent = `${res.metadata.reading_time} min`;
        if (metaModel) metaModel.textContent = res.model_used;

        if (tagsCloud) {
            tagsCloud.innerHTML = res.keywords.map(kw => `<span class="tag-chip">${kw}</span>`).join('');
        }

        if (pdfReportLink) {
            pdfReportLink.href = `/report/${res.id}`;
        }

        resultCard.classList.remove('hidden');
    }

    // Copy Summary Button
    const btnCopyResult = document.getElementById('btnCopyResult');
    if (btnCopyResult) {
        btnCopyResult.addEventListener('click', () => {
            const badgeText = document.getElementById('resultBadge')?.innerText || '';
            const confText = document.getElementById('confidenceValue')?.innerText || '';
            const textToCopy = `VeriNews AI Analysis Result:\nPrediction: ${badgeText}\nConfidence: ${confText}`;

            navigator.clipboard.writeText(textToCopy).then(() => {
                const originalText = btnCopyResult.innerHTML;
                btnCopyResult.innerHTML = `<i class="fa-solid fa-check"></i> Copied!`;
                setTimeout(() => {
                    btnCopyResult.innerHTML = originalText;
                }, 2000);
            });
        });
    }
});
