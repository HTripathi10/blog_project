import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useEditor, EditorContent } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import Image from '@tiptap/extension-image'
import { postsApi } from '../api/posts'
import toast from 'react-hot-toast'

export default function PostEditor() {
  const { id } = useParams()
  const isEditing = Boolean(id)
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors },
  } = useForm({
    defaultValues: {
      title: '',
      tags: '',
    },
  })

  const editor = useEditor({
    extensions: [
      StarterKit,
      Image.configure({
        inline: true,
        allowBase64: true,
      }),
    ],
    content: '',
    editorProps: {
      attributes: {
        class: 'editor-content',
      },
    },
    onUpdate: ({ editor }) => {
      setContent(editor.getHTML())
    },
  })

  const [content, setContent] = useState('')
  const [coverImageUrl, setCoverImageUrl] = useState('')
  const [coverUploading, setCoverUploading] = useState(false)

  const handleImageUpload = () => {
    const input = document.createElement('input')
    input.type = 'file'
    input.accept = 'image/*'
    input.onchange = (e) => {
      const file = e.target.files[0]
      if (file) {
        const reader = new FileReader()
        reader.onload = () => {
          if (editor) {
            editor.chain().focus().setImage({ src: reader.result }).run()
          }
        }
        reader.readAsDataURL(file)
      }
    }
    input.click()
  }

  const handleCoverUpload = async (event) => {
    const file = event.target.files?.[0]
    if (!file) return
    setCoverUploading(true)
    try {
      const res = await postsApi.uploadCover(file)
      setCoverImageUrl(res.data.url)
      toast.success('Header image uploaded')
    } catch (err) {
      const detail = err.response?.data?.detail
      toast.error(typeof detail === 'string' ? detail : 'Failed to upload header image')
    } finally {
      setCoverUploading(false)
      event.target.value = ''
    }
  }

  // Fetch existing post if editing
  const { data: postData, isLoading: isFetchingPost } = useQuery({
    queryKey: ['post', id],
    queryFn: async () => {
      const res = await postsApi.get(id)
      return res.data
    },
    enabled: isEditing,
  })

  useEffect(() => {
    if (postData) {
      setValue('title', postData.title || '')
      setCoverImageUrl(postData.cover_image_url || '')
      setContent(postData.content || '')
      if (editor) {
        editor.commands.setContent(postData.content || '')
      }
      const tagList = Array.isArray(postData.tags)
        ? postData.tags.map((t) => (typeof t === 'object' ? t.name : t)).join(', ')
        : ''
      setValue('tags', tagList)
    }
  }, [postData, setValue, editor])

  const isDraft = postData?.status === 'draft'

  const saveMutation = useMutation({
    mutationFn: ({ data, status }) => {
      const payload = {
        title: data.title.trim(),
        content: content.trim(),
        cover_image_url: coverImageUrl || null,
        status,
        tags: data.tags
          ? data.tags
              .split(',')
              .map((t) => t.trim().toLowerCase())
              .filter(Boolean)
          : [],
      }
      return isEditing ? postsApi.update(id, payload) : postsApi.create(payload)
    },
    onSuccess: (res, variables) => {
      const savedPost = res.data
      const status = variables.status
      const message = status === 'published'
        ? (isEditing ? 'Post updated successfully!' : 'Post published successfully! 🎉')
        : (isEditing ? 'Draft updated!' : 'Draft saved!')
      toast.success(message)
      queryClient.invalidateQueries({ queryKey: ['posts'] })
      if (isEditing) {
        queryClient.invalidateQueries({ queryKey: ['post', id] })
      }
      if (status === 'published') {
        const targetId = savedPost?.id || savedPost?._id || id
        navigate(targetId ? `/posts/${targetId}` : '/')
      } else {
        navigate('/profile')
      }
    },
    onError: (err) => {
      const detail = err.response?.data?.detail
      const msg = Array.isArray(detail)
        ? detail.map((d) => d.msg).join(', ')
        : typeof detail === 'string'
        ? detail
        : 'Failed to save post'
      toast.error(msg)
    },
  })

  const onSubmit = (formData, status = 'published') => {
    if (!content.trim()) {
      toast.error('Article content cannot be empty')
      return
    }
    if (content.trim().length < 10) {
      toast.error('Content must be at least 10 characters')
      return
    }
    saveMutation.mutate({ data: formData, status })
  }

  if (isEditing && isFetchingPost) {
    return (
      <div className="container" style={{ padding: '4rem 1.5rem', textAlign: 'center' }}>
        <div className="spinner" style={{ margin: '0 auto 1rem' }}></div>
        <p className="text-muted">Loading article data...</p>
      </div>
    )
  }

  return (
    <div className="post-editor-page container">
      <div className="editor-header">
        <div>
          <Link to="/" className="back-link">
            ← Cancel & Back
          </Link>
          <h1 className="editor-title">{isEditing ? 'Edit Article' : 'Write New Article'}</h1>
        </div>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="editor-form">
        <div className="form-group">
          <input
            type="text"
            className={`input editor-title-input ${errors.title ? 'input-error' : ''}`}
            placeholder="Article Title..."
            {...register('title', {
              required: 'Title is required',
              minLength: { value: 3, message: 'Title must be at least 3 characters' },
            })}
          />
          {errors.title && <p className="form-error">{errors.title.message}</p>}
        </div>

        <div className="form-group">
          <label className="form-label">Header image</label>
          <div className={`cover-uploader ${coverImageUrl ? 'cover-uploader--filled' : ''}`}>
            {coverImageUrl ? (
              <img src={coverImageUrl} alt="Header preview" className="cover-uploader__preview" />
            ) : (
              <div className="cover-uploader__empty">
                <strong>Upload a header image</strong>
                <span>JPEG, PNG, GIF or WebP — this is what readers see first.</span>
              </div>
            )}
            <div className="cover-uploader__actions">
              <label className="btn btn--secondary btn--sm">
                {coverUploading ? 'Uploading...' : coverImageUrl ? 'Replace image' : 'Choose image'}
                <input
                  type="file"
                  accept="image/jpeg,image/png,image/gif,image/webp"
                  hidden
                  onChange={handleCoverUpload}
                  disabled={coverUploading}
                />
              </label>
              {coverImageUrl && (
                <button
                  type="button"
                  className="btn btn--ghost btn--sm"
                  onClick={() => setCoverImageUrl('')}
                >
                  Remove
                </button>
              )}
            </div>
          </div>
        </div>

        <div className="form-group">
          <label className="form-label" htmlFor="tags">
            Tags (comma separated, e.g. python, react, ai)
          </label>
          <input
            id="tags"
            type="text"
            className="input"
            placeholder="e.g. react, python, webdev"
            {...register('tags')}
          />
        </div>

        <div className="editor-content-area">
          <div className="editor-toolbar">
            <button
              type="button"
              onClick={() => editor?.chain().focus().toggleBold().run()}
              className={`toolbar-btn ${editor?.isActive('bold') ? 'active' : ''}`}
              title="Bold"
            >
              <strong>B</strong>
            </button>
            <button
              type="button"
              onClick={() => editor?.chain().focus().toggleItalic().run()}
              className={`toolbar-btn ${editor?.isActive('italic') ? 'active' : ''}`}
              title="Italic"
            >
              <em>I</em>
            </button>
            <button
              type="button"
              onClick={() => editor?.chain().focus().toggleHeading({ level: 2 }).run()}
              className={`toolbar-btn ${editor?.isActive('heading', { level: 2 }) ? 'active' : ''}`}
              title="Heading"
            >
              H
            </button>
            <button
              type="button"
              onClick={() => editor?.chain().focus().toggleCode().run()}
              className={`toolbar-btn ${editor?.isActive('code') ? 'active' : ''}`}
              title="Code"
            >
              {'<>'}
            </button>
            <button
              type="button"
              onClick={() => editor?.chain().focus().toggleCodeBlock().run()}
              className={`toolbar-btn ${editor?.isActive('codeBlock') ? 'active' : ''}`}
              title="Code Block"
            >
              {'{ }'}
            </button>
            <button
              type="button"
              onClick={() => editor?.chain().focus().toggleBlockquote().run()}
              className={`toolbar-btn ${editor?.isActive('blockquote') ? 'active' : ''}`}
              title="Quote"
            >
              ❝
            </button>
            <button
              type="button"
              onClick={() => editor?.chain().focus().toggleBulletList().run()}
              className={`toolbar-btn ${editor?.isActive('bulletList') ? 'active' : ''}`}
              title="Bullet List"
            >
              • List
            </button>
            <button
              type="button"
              onClick={() => editor?.chain().focus().toggleOrderedList().run()}
              className={`toolbar-btn ${editor?.isActive('orderedList') ? 'active' : ''}`}
              title="Numbered List"
            >
              1. List
            </button>
            <button
              type="button"
              onClick={handleImageUpload}
              className="toolbar-btn"
              title="Insert Image"
            >
              🖼️
            </button>
          </div>
          <div className="editor-wrapper">
            <EditorContent editor={editor} />
          </div>
        </div>

        <div className="editor-footer">
          <div className="editor-actions">
            <button
              type="button"
              className="btn btn--secondary"
              onClick={() => navigate(-1)}
              disabled={saveMutation.isPending}
            >
              Cancel
            </button>
            <button
              type="button"
              className="btn btn--ghost"
              onClick={handleSubmit((data) => onSubmit(data, 'draft'))}
              disabled={saveMutation.isPending}
            >
              {saveMutation.isPending ? 'Saving...' : 'Save as Draft'}
            </button>
            <button
              type="button"
              className="btn btn--primary"
              onClick={handleSubmit((data) => onSubmit(data, 'published'))}
              disabled={saveMutation.isPending}
            >
              {saveMutation.isPending
                ? 'Publishing...'
                : isEditing && isDraft
                ? 'Update and Publish'
                : isEditing
                ? 'Update Article'
                : 'Publish Article'}
            </button>
          </div>
        </div>
      </form>
    </div>
  )
}
