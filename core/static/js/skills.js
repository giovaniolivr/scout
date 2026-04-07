/**
 * skills.js — Reusable skill input components for Scout.
 *
 * Public API:
 *   initSkillTagInput(containerId, hiddenId, skillList, tagClass, existingValues)
 *   initHardSkillsInput(containerId, hiddenId, existingValues)
 *   initSoftSkillsInput(containerId, hiddenId, existingValues)
 */

// ---------------------------------------------------------------------------
// Canonical data — must stay in sync with core/skills.py
// ---------------------------------------------------------------------------

const HARD_SKILLS = [
  'C','C#','C++','Clojure','Dart','Elixir','Go','Haskell','Java',
  'JavaScript','Kotlin','Lua','MATLAB','Perl','PHP','Python','R',
  'Ruby','Rust','Scala','Swift','TypeScript',
  'ASP.NET','Django','Express.js','FastAPI','Flask','Laravel',
  'NestJS','Node.js','Ruby on Rails','Spring Boot','Symfony',
  'Angular','Bootstrap','CSS','HTML','jQuery','Next.js','Nuxt.js',
  'React','Sass','Svelte','Tailwind CSS','Vue.js',
  'Android','Flutter','iOS','React Native',
  'Cassandra','DynamoDB','Elasticsearch','Firebase','MongoDB',
  'MySQL','Oracle','PostgreSQL','Redis','SQL','SQL Server','SQLite',
  'Ansible','Apache','AWS','Azure','Bash','CI/CD','Docker',
  'Git','GitHub','GitHub Actions','GitLab','Google Cloud',
  'Jenkins','Kubernetes','Linux','Nginx','Terraform',
  'Airflow','dbt','Deep Learning','Excel Avançado','Hadoop',
  'Machine Learning','Matplotlib','NumPy','Pandas','Power BI',
  'PyTorch','scikit-learn','Spark','Tableau','TensorFlow',
  'gRPC','GraphQL','Kafka','Message Queues','Microsserviços',
  'RabbitMQ','REST APIs','WebSockets',
  'Cypress','Jest','JUnit','Playwright','Pytest','Selenium',
  'Adobe XD','Figma','Illustrator','InDesign','Photoshop',
  'Prototyping','Sketch',
  'Unity','Unreal Engine',
  'Confluence','Excel','Google Workspace','Jira','Kanban','Notion',
  'PowerPoint','Salesforce','SAP','Scrum','Agile','Trello','Word',
];

const SOFT_SKILL_CATEGORIES = [
  'Comunicação','Comunicação Técnica','Comunicação Interpessoal',
  'Comunicação Escrita','Apresentação e Oratória','Escuta Ativa',
  'Feedback Construtivo',
  'Liderança','Gestão de Equipes','Mentoria e Coaching','Delegação',
  'Desenvolvimento de Pessoas','Gestão de Conflitos',
  'Influência e Persuasão','Tomada de Decisão',
  'Trabalho em Equipe','Colaboração','Empatia','Escuta Empática',
  'Construção de Relacionamentos','Networking',
  'Resolução de Problemas','Pensamento Analítico','Pensamento Crítico',
  'Raciocínio Lógico','Criatividade','Inovação','Pensamento Lateral',
  'Gestão do Tempo','Organização','Planejamento','Priorização',
  'Gestão de Projetos','Atenção aos Detalhes','Multitarefa',
  'Adaptabilidade','Flexibilidade','Resiliência','Aprendizado Contínuo',
  'Gestão de Mudanças','Tolerância à Ambiguidade',
  'Inteligência Emocional','Autoconhecimento','Autocontrole',
  'Motivação','Gestão do Estresse','Consciência Social',
  'Proatividade','Iniciativa','Ética Profissional','Comprometimento',
  'Responsabilidade','Autonomia','Foco em Resultados',
  'Orientação para o Cliente','Pontualidade',
  'Negociação','Argumentação','Gestão de Expectativas',
  'Resolução de Impasses',
  'Visão Estratégica','Pensamento Sistêmico','Visão de Negócio',
  'Orientação para Dados','Gestão de Riscos',
];

// ---------------------------------------------------------------------------
// Generic tag input initializer
// ---------------------------------------------------------------------------

function initSkillTagInput(containerId, hiddenId, skillList, tagClass, existingValues) {
  var container = document.getElementById(containerId);
  var hidden    = document.getElementById(hiddenId);
  if (!container || !hidden) return;

  var selected = (existingValues || []).filter(Boolean);
  var tagsEl   = container.querySelector('.skill-tags-selected');
  var input    = container.querySelector('.skill-search-input');
  var dropdown = container.querySelector('.skill-dropdown');

  function syncHidden() {
    hidden.value = selected.join(', ');
  }

  function renderTags() {
    tagsEl.innerHTML = '';
    selected.forEach(function(skill) {
      var tag = document.createElement('span');
      tag.className = 'skill-tag ' + tagClass + ' skill-input-tag';
      tag.innerHTML =
        escapeHtml(skill) +
        ' <button type="button" class="skill-tag-remove" data-skill="' +
        escapeHtml(skill) + '" aria-label="Remover ' + escapeHtml(skill) +
        '">&times;</button>';
      tagsEl.appendChild(tag);
    });
    syncHidden();
  }

  function buildDropdown(matches) {
    dropdown.innerHTML = '';
    if (matches.length === 0) {
      var none = document.createElement('div');
      none.className = 'skill-dropdown-empty';
      none.textContent = 'Nenhum resultado encontrado.';
      dropdown.appendChild(none);
    } else {
      matches.forEach(function(skill) {
        var item = document.createElement('div');
        item.className = 'skill-dropdown-item';
        item.textContent = skill;
        item.addEventListener('mousedown', function(e) {
          e.preventDefault();
          addSkill(skill);
        });
        dropdown.appendChild(item);
      });
    }
    dropdown.style.display = 'block';
  }

  function showDropdown(query) {
    var q = query.toLowerCase().trim();
    var matches;
    if (q === '') {
      // Show all unselected skills when query is empty (click to browse)
      matches = skillList.filter(function(s) {
        return selected.indexOf(s) === -1;
      });
    } else {
      matches = skillList.filter(function(s) {
        return s.toLowerCase().indexOf(q) !== -1 && selected.indexOf(s) === -1;
      });
    }
    buildDropdown(matches);
  }

  function addSkill(skill) {
    if (selected.indexOf(skill) === -1) {
      selected.push(skill);
      renderTags();
    }
    input.value = '';
    dropdown.style.display = 'none';
    input.focus();
  }

  // Remove tag on × click
  tagsEl.addEventListener('click', function(e) {
    var btn = e.target.closest('.skill-tag-remove');
    if (btn) {
      var skill = btn.dataset.skill;
      selected = selected.filter(function(s) { return s !== skill; });
      renderTags();
    }
  });

  // Focus input when clicking the container background
  container.addEventListener('click', function(e) {
    if (!e.target.closest('.skill-tag-remove')) input.focus();
  });

  input.addEventListener('focus', function() {
    showDropdown(input.value);
  });

  input.addEventListener('input', function() {
    showDropdown(input.value);
  });

  input.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
      dropdown.style.display = 'none';
      input.blur();
    }
    if (e.key === 'Enter') {
      e.preventDefault();
      var first = dropdown.querySelector('.skill-dropdown-item');
      if (first) addSkill(first.textContent);
    }
    if (e.key === 'Backspace' && input.value === '' && selected.length > 0) {
      selected.pop();
      renderTags();
    }
  });

  input.addEventListener('blur', function() {
    setTimeout(function() { dropdown.style.display = 'none'; }, 160);
  });

  renderTags();
}

// ---------------------------------------------------------------------------
// Convenience wrappers
// ---------------------------------------------------------------------------

function initHardSkillsInput(containerId, hiddenId, existingValues) {
  initSkillTagInput(containerId, hiddenId, HARD_SKILLS, 'skill-tag--hard', existingValues);
}

function initSoftSkillsInput(containerId, hiddenId, existingValues) {
  initSkillTagInput(containerId, hiddenId, SOFT_SKILL_CATEGORIES, 'skill-tag--soft', existingValues);
}

// ---------------------------------------------------------------------------
// Utility
// ---------------------------------------------------------------------------

function escapeHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function parseSkillValue(hiddenId) {
  var el = document.getElementById(hiddenId);
  if (!el || !el.value.trim()) return [];
  return el.value.split(',').map(function(s) { return s.trim(); }).filter(Boolean);
}

// ---------------------------------------------------------------------------
// Auto-init when the standard elements are present on the page
// ---------------------------------------------------------------------------

document.addEventListener('DOMContentLoaded', function() {
  if (document.getElementById('hardSkillsContainer')) {
    initHardSkillsInput(
      'hardSkillsContainer',
      'hardSkillsValue',
      parseSkillValue('hardSkillsValue')
    );
  }
  if (document.getElementById('softSkillsContainer')) {
    initSoftSkillsInput(
      'softSkillsContainer',
      'softSkillsValue',
      parseSkillValue('softSkillsValue')
    );
  }
});
