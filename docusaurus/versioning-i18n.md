# Versioning and Internationalization

Docusaurus provides built-in support for documentation versioning and multi-language sites (i18n).

## Documentation Versioning

Versioning allows you to maintain multiple versions of your documentation, useful when supporting multiple product releases.

### Creating a Version

```bash
# Create a new version from current docs
npm run docusaurus docs:version 1.0.0
```

This creates:
- `versioned_docs/version-1.0.0/` - Snapshot of your docs
- `versioned_sidebars/version-1.0.0-sidebars.json` - Sidebar snapshot
- Updates `versions.json` with the new version

### Version Structure

```
website/
├── docs/                          # "Next" version (unreleased)
│   └── intro.md
├── versioned_docs/
│   ├── version-2.0.0/
│   │   └── intro.md
│   └── version-1.0.0/
│       └── intro.md
├── versioned_sidebars/
│   ├── version-2.0.0-sidebars.json
│   └── version-1.0.0-sidebars.json
├── versions.json                   # ["2.0.0", "1.0.0"]
└── sidebars.js                     # Sidebar for "next" version
```

### versions.json

Lists available versions in order (newest first):

```json
["2.0.0", "1.0.0"]
```

### URL Paths

| Version | URL Path |
|---------|----------|
| Current/Latest (e.g., 2.0.0) | `/docs/intro` |
| Next (unreleased) | `/docs/next/intro` |
| Older (e.g., 1.0.0) | `/docs/1.0.0/intro` |

### Configuration Options

```typescript
docs: {
  // Show "last updated" info
  showLastUpdateAuthor: true,
  showLastUpdateTime: true,

  // Version behavior
  lastVersion: 'current',           // Or specific version like '2.0.0'
  includeCurrentVersion: true,      // Include /docs/next/

  // Only include specific versions
  onlyIncludeVersions: ['2.0.0', '1.0.0'],

  // Version-specific config
  versions: {
    current: {
      label: 'Next',
      path: 'next',
      banner: 'unreleased',         // 'none' | 'unreleased' | 'unmaintained'
    },
    '2.0.0': {
      label: '2.0.0',
      path: '',                     // Serve at /docs/ root
      badge: true,                  // Show version badge
    },
    '1.0.0': {
      label: '1.0.0 (Legacy)',
      path: '1.0.0',
      banner: 'unmaintained',
    },
  },
}
```

### Version Dropdown

Add to navbar:

```typescript
navbar: {
  items: [
    {
      type: 'docsVersionDropdown',
      position: 'right',
      dropdownItemsAfter: [
        { to: '/versions', label: 'All versions' },
      ],
      dropdownActiveClassDisabled: true,
    },
  ],
}
```

### Version Banner

Automatically shown based on `banner` config. Customize message:

```typescript
versions: {
  '1.0.0': {
    banner: 'unmaintained',
    // Custom banner handled via theme customization
  },
}
```

### Linking Between Versions

```markdown
<!-- Link to specific version -->
[See v1.0 docs](/docs/1.0.0/intro)

<!-- Link to current version (version-agnostic) -->
[See latest docs](/docs/intro)
```

### Best Practices for Versioning

1. **Version sparingly** - Each version increases maintenance burden
2. **Maintain minimal versions** - Archive or remove old versions
3. **Use version banners** - Clearly indicate unmaintained versions
4. **Keep docs in sync** - Apply fixes to all relevant versions
5. **Document breaking changes** - Use migration guides

---

## Internationalization (i18n)

Docusaurus supports multi-language documentation with a git-based workflow.

### Configuration

```typescript
// docusaurus.config.ts
const config: Config = {
  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'fr', 'ja', 'zh-Hans'],
    localeConfigs: {
      en: {
        label: 'English',
        htmlLang: 'en-US',
        direction: 'ltr',
        calendar: 'gregory',
        path: 'en',
      },
      fr: {
        label: 'Français',
        htmlLang: 'fr-FR',
        direction: 'ltr',
      },
      ja: {
        label: '日本語',
        htmlLang: 'ja',
      },
      'zh-Hans': {
        label: '简体中文',
        htmlLang: 'zh-Hans',
      },
      ar: {
        label: 'العربية',
        htmlLang: 'ar',
        direction: 'rtl',  // Right-to-left
      },
    },
  },
};
```

### i18n Directory Structure

```
website/
├── docs/                                # Default locale content
│   └── intro.md
├── blog/
│   └── 2024-01-01-post.md
├── i18n/
│   ├── fr/                              # French translations
│   │   ├── docusaurus-plugin-content-docs/
│   │   │   ├── current/                 # Translated docs
│   │   │   │   └── intro.md
│   │   │   └── current.json             # Sidebar label translations
│   │   ├── docusaurus-plugin-content-blog/
│   │   │   └── 2024-01-01-post.md
│   │   ├── docusaurus-theme-classic/
│   │   │   ├── navbar.json              # Navbar translations
│   │   │   └── footer.json              # Footer translations
│   │   └── code.json                    # Theme UI string translations
│   └── ja/
│       └── ...
└── docusaurus.config.ts
```

### Generating Translation Files

```bash
# Generate translation files for French
npm run docusaurus write-translations -- --locale fr
```

This creates JSON files for translatable strings.

### Translation JSON Files

**code.json** - Theme UI strings:

```json
{
  "theme.common.skipToMainContent": {
    "message": "Aller au contenu principal",
    "description": "The skip to content label"
  },
  "theme.docs.sidebar.collapseButtonTitle": {
    "message": "Réduire la barre latérale",
    "description": "Sidebar collapse button title"
  }
}
```

**navbar.json** - Navbar items:

```json
{
  "title": {
    "message": "Mon Site",
    "description": "The site title"
  },
  "item.label.Docs": {
    "message": "Documentation",
    "description": "Navbar item label"
  }
}
```

**current.json** - Sidebar labels:

```json
{
  "sidebar.docs.category.Getting Started": {
    "message": "Premiers pas",
    "description": "Sidebar category label"
  }
}
```

### Translating Docs

Copy and translate markdown files:

```bash
# Copy docs to translate
mkdir -p i18n/fr/docusaurus-plugin-content-docs/current
cp -r docs/* i18n/fr/docusaurus-plugin-content-docs/current/
```

Then translate the content in the copied files.

### Locale Dropdown

Add to navbar:

```typescript
navbar: {
  items: [
    {
      type: 'localeDropdown',
      position: 'right',
      dropdownItemsAfter: [
        {
          href: 'https://crowdin.com/project/my-docs',
          label: 'Help translate',
        },
      ],
    },
  ],
}
```

### Development with Locales

```bash
# Start dev server with specific locale
npm run start -- --locale fr

# Build for specific locale
npm run build -- --locale fr

# Build all locales
npm run build
```

### URL Paths

| Locale | URL Path |
|--------|----------|
| Default (en) | `/docs/intro` |
| French | `/fr/docs/intro` |
| Japanese | `/ja/docs/intro` |

### Translation Management with Crowdin

1. Install Crowdin CLI:
```bash
npm install @crowdin/cli -D
```

2. Create `crowdin.yml`:
```yaml
project_id: 'YOUR_PROJECT_ID'
api_token_env: 'CROWDIN_TOKEN'
base_path: '.'
base_url: 'https://api.crowdin.com'

files:
  - source: /i18n/en/**/*
    translation: /i18n/%two_letters_code%/**/%original_file_name%
```

3. Upload/download translations:
```bash
# Upload source files to Crowdin
npx crowdin upload

# Download translations from Crowdin
npx crowdin download
```

### Linking Between Locales

Use the `useDocusaurusContext` hook:

```jsx
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Link from '@docusaurus/Link';

function LocalizedLink() {
  const { i18n } = useDocusaurusContext();
  const { currentLocale } = i18n;

  return (
    <Link to={`/${currentLocale}/docs/intro`}>
      Go to intro
    </Link>
  );
}
```

### Best Practices for i18n

1. **Start with structure** - Set up i18n early in the project
2. **Use translation management** - Tools like Crowdin simplify collaboration
3. **Keep content in sync** - Update all locales when source changes
4. **Provide fallbacks** - Untranslated content falls back to default locale
5. **Test RTL** - Verify layouts work for RTL languages
6. **Consider partial translation** - It's OK to launch with incomplete translations

### Combining Versioning and i18n

Structure for versioned, multi-locale docs:

```
i18n/
└── fr/
    └── docusaurus-plugin-content-docs/
        ├── current/           # French "next" docs
        ├── current.json
        ├── version-2.0.0/     # French v2.0.0 docs
        ├── version-2.0.0.json
        ├── version-1.0.0/     # French v1.0.0 docs
        └── version-1.0.0.json
```

URLs:
- `/docs/intro` - English latest
- `/fr/docs/intro` - French latest
- `/fr/docs/1.0.0/intro` - French v1.0.0
