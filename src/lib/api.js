import { supabase } from './supabase'

// ========================
// Visa Applications
// ========================

export async function createApplication(applicationData) {
  const { data, error } = await supabase
    .from('visa_applications')
    .insert([applicationData])
    .select()
    .single()
  return { data, error }
}

export async function getApplications() {
  const { data, error } = await supabase
    .from('visa_applications')
    .select('*')
    .order('created_at', { ascending: false })
  return { data, error }
}

export async function getApplication(id) {
  const { data, error } = await supabase
    .from('visa_applications')
    .select('*')
    .eq('id', id)
    .single()
  return { data, error }
}

export async function updateApplication(id, updates) {
  const { data, error } = await supabase
    .from('visa_applications')
    .update(updates)
    .eq('id', id)
    .select()
    .single()
  return { data, error }
}

export async function deleteApplication(id) {
  const { error } = await supabase
    .from('visa_applications')
    .delete()
    .eq('id', id)
  return { error }
}

// ========================
// Documents
// ========================

export async function uploadDocument(applicationId, file, documentType) {
  // Upload file to storage
  const filePath = `${applicationId}/${Date.now()}_${file.name}`
  const { data: storageData, error: storageError } = await supabase.storage
    .from('documents')
    .upload(filePath, file)

  if (storageError) return { error: storageError }

  // Get public URL
  const { data: { publicUrl } } = supabase.storage
    .from('documents')
    .getPublicUrl(filePath)

  // Create document record
  const { data, error } = await supabase
    .from('documents')
    .insert([{
      application_id: applicationId,
      file_name: file.name,
      file_url: publicUrl,
      document_type: documentType,
      status: 'pending',
    }])
    .select()
    .single()

  return { data, error }
}

export async function getDocuments(applicationId) {
  const { data, error } = await supabase
    .from('documents')
    .select('*')
    .eq('application_id', applicationId)
    .order('created_at', { ascending: false })
  return { data, error }
}

export async function getDocument(id) {
  const { data, error } = await supabase
    .from('documents')
    .select('*, document_classifications(*)')
    .eq('id', id)
    .single()
  return { data, error }
}

// ========================
// Document Classifications
// ========================

export async function getClassification(documentId) {
  const { data, error } = await supabase
    .from('document_classifications')
    .select('*')
    .eq('document_id', documentId)
    .single()
  return { data, error }
}

export async function getApplicationClassifications(applicationId) {
  const { data, error } = await supabase
    .from('document_classifications')
    .select(`
      *,
      document:documents!inner(*)
    `)
    .eq('document.application_id', applicationId)
  return { data, error }
}

// ========================
// Stats / Dashboard
// ========================

export async function getDashboardStats() {
  const { data: applications, error: appError } = await supabase
    .from('visa_applications')
    .select('*')

  if (appError) return { error: appError }

  const total = applications?.length || 0
  const inProgress = applications?.filter(a => a.status === 'in_progress').length || 0
  const verified = applications?.filter(a => a.status === 'verified').length || 0
  const rejected = applications?.filter(a => a.status === 'rejected').length || 0
  const avgScore = applications?.length
    ? Math.round(applications.reduce((sum, a) => sum + (a.overall_score || 0), 0) / applications.length)
    : 0

  return {
    data: { total, inProgress, verified, rejected, avgScore },
    error: null,
  }
}