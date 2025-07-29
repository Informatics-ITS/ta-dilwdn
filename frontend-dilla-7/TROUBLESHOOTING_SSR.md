# 🔧 Troubleshooting SSR Issues - Frontend

Dokumentasi untuk mengatasi masalah SSR (Server-Side Rendering) dan error Svelte yang ditemukan.

## 🚨 **Masalah yang Ditemukan**

### **1. Vite SSR Timeout Error**
```
Error when evaluating SSR module: transport invoke timed out after 60000ms
```

**Penyebab:**
- Async operations dalam `onMount` yang terlalu lama
- API calls yang di-await di SSR context
- Complex reactive statements yang dieksekusi di server

**Solusi:**
```typescript
// ❌ Problematic
onMount(async () => {
  await loadData(); // Causes SSR timeout
});

// ✅ Fixed
onMount(() => {
  if (!browser) return;
  loadData(); // No await in onMount
});
```

### **2. Svelte `{@const}` Placement Error**
```
`{@const}` must be the immediate child of `{#if}`, `{:else if}`, `{:else}`, `{#each}`, etc.
```

**Penyebab:**
- `{@const}` ditempatkan di dalam `<div>` bukan langsung di dalam control flow

**Solusi:**
```svelte
<!-- ❌ Problematic -->
{#if condition}
  <div>
    {@const variable = computation()}
  </div>
{/if}

<!-- ✅ Fixed -->
{#if condition}
  {@const variable = computation()}
  <div>
    <!-- Use variable here -->
  </div>
{/if}
```

## 🛠️ **Implementasi Perbaikan**

### **1. SSR-Safe Component Loading**

#### **Server Load Function (`+page.server.ts`):**
```typescript
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params }) => {
  // Minimal server processing, no API calls
  return {
    ujianSiswaId: parseInt(params.id) || null
  };
};
```

#### **Client-Side Data Loading:**
```typescript
import { browser } from '$app/environment';

export let data: PageData;
let ujianSiswaId: number = data.ujianSiswaId || 0;

onMount(() => {
  if (!browser) return; // Skip on server
  
  if (!ujianSiswaId || isNaN(ujianSiswaId)) {
    error = 'ID ujian siswa tidak valid';
    loading = false;
    return;
  }

  loadData(); // Client-side only
});
```

### **2. Browser-Safe Reactive Statements**

```typescript
// ❌ Problematic - runs on server
$: processedData = data ? computeData(data) : null;

// ✅ Fixed - browser only
let processedData: any = null;

$: if (data && browser) {
  processedData = computeData(data);
}
```

### **3. Safe JSON Parsing**

```typescript
// Wrapped dalam try-catch dan IIFE
{@const safeData = (() => {
  try {
    return JSON.parse(item.json_data || '{}');
  } catch (e) {
    return { fallback: 'data' };
  }
})()}
```

### **4. Conditional Component Rendering**

```svelte
<!-- Render complex components only in browser -->
{#if browser && dataReady}
  <ComplexComponent {props} />
{:else if !browser}
  <div class="animate-pulse">Loading...</div>
{:else}
  <ErrorComponent />
{/if}
```

## 🎯 **Best Practices untuk SSR**

### **1. Data Loading Strategy**
- ✅ Server: Minimal data, no API calls
- ✅ Client: API calls dalam `onMount`
- ✅ Fallback: Loading states untuk SSR

### **2. Component Architecture**
- ✅ Wrap heavy components dengan `{#if browser}`
- ✅ Provide loading states untuk SSR
- ✅ Handle async operations dengan error boundaries

### **3. Error Handling**
- ✅ Try-catch untuk JSON parsing
- ✅ Fallback values untuk computed data
- ✅ Graceful degradation untuk complex UI

### **4. Performance Optimization**
- ✅ Lazy load heavy components
- ✅ Split complex calculations
- ✅ Use browser checks for client-only code

## 🧪 **Testing Checklist**

### **1. SSR Testing**
- [ ] Page loads without JavaScript
- [ ] No console errors on server
- [ ] Proper fallback rendering
- [ ] Loading states work correctly

### **2. Client Hydration**
- [ ] Components render after hydration
- [ ] API calls execute properly
- [ ] State management works
- [ ] Navigation functions correctly

### **3. Error Scenarios**
- [ ] Invalid route parameters
- [ ] API failures
- [ ] JSON parsing errors
- [ ] Network timeouts

## 🔍 **Debug Tools**

### **1. Browser Detection**
```typescript
import { browser } from '$app/environment';

console.log('Running in browser:', browser);
```

### **2. SSR Debug**
```svelte
{#if !browser}
  <div>SSR Mode</div>
{:else}
  <div>Client Mode</div>
{/if}
```

### **3. API Debug**
```typescript
async function loadData() {
  try {
    console.log('Loading data for ID:', ujianSiswaId);
    const data = await api.get(`/endpoint/${ujianSiswaId}`);
    console.log('Data loaded:', data);
  } catch (error) {
    console.error('API Error:', error);
  }
}
```

## 📋 **Fixed Files Summary**

### **1. Backend Files:**
- ✅ `backend/app.py` - Stored procedure endpoints
- ✅ `backend/stored_procedures.sql` - Database procedures
- ✅ `backend/reset_database.py` - Auto-create procedures

### **2. Frontend Files:**
- ✅ `frontend/src/lib/components/ComparisonRecommendations.svelte` - Fixed `{@const}` placement
- ✅ `frontend/src/routes/dashboard/laporan/ujian-siswa/[id]/+page.svelte` - SSR fixes
- ✅ `frontend/src/routes/dashboard/laporan/ujian-siswa/[id]/+page.server.ts` - Server load
- ✅ `frontend/src/lib/api/stored-procedure.ts` - API service

### **3. Key Changes:**
1. **SSR Safety**: Added `browser` checks
2. **Error Handling**: Try-catch wrapping
3. **Async Operations**: Moved to client-side only
4. **Component Loading**: Conditional rendering
5. **Data Flow**: Server → Client separation

## 🚀 **Deployment Checklist**

- [ ] Test SSR in production build
- [ ] Verify API endpoints work
- [ ] Check error handling
- [ ] Test all routes
- [ ] Performance monitoring
- [ ] Browser compatibility

---

**Status**: ✅ **RESOLVED**  
**Last Updated**: January 2024  
**Issues Fixed**: SSR Timeout, Svelte const placement, API loading 