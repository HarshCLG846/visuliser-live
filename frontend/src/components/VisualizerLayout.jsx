import React, { useState, useEffect } from 'react'
import LeftCategorySidebar, { categoryData } from './LeftCategorySidebar'
import ImageCanvas from './ImageCanvas'
import RightActionSidebar from './RightActionSidebar'
import DetectionResultsPanel from './DetectionResultsPanel'
import AnalysisResultModal from './AnalysisResultModal'
import Loader from './Loader'
import { productData } from './ProductData'
import { analyzeExterior, checkHealth, editImage } from '../services/api'
import ConnectionStatus from './ConnectionStatus'
import './VisualizerLayout.css'

function VisualizerLayout() {
  const [activeCategory, setActiveCategory] = useState(null)
  const [houseImage, setHouseImage] = useState(null)
  const [imageFile, setImageFile] = useState(null)
  const [selectedItems, setSelectedItems] = useState([]) // Array of selected items: ['roof', 'siding', 'trim']
  const [selectedProducts, setSelectedProducts] = useState({}) // Product details for each item
  const [analysisResults, setAnalysisResults] = useState(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [apiError, setApiError] = useState(null)
  const [apiConnected, setApiConnected] = useState(false)
  const [editedImage, setEditedImage] = useState(null)
  const [isEditing, setIsEditing] = useState(false)
  const [viewMode, setViewMode] = useState('original') // 'original' or 'edited'
  const [showAnalysisModal, setShowAnalysisModal] = useState(false)

  // Check API health on mount
  useEffect(() => {
    checkHealth().then((result) => {
      setApiConnected(result.status === 'ok')
    }).catch(() => {
      setApiConnected(false)
    })
  }, [])

  const handleCategoryChange = (category) => {
    // Toggle: if same category is clicked, hide the panel
    if (activeCategory === category) {
      setActiveCategory(null)
    } else {
      setActiveCategory(category)
    }
  }

  const handleImageUpload = (file) => {
    if (file) {
      setImageFile(file)
      setApiError(null)
      setAnalysisResults(null)
      setEditedImage(null)
      setViewMode('original')

      // Display image immediately
      // TODO: Add backend validation API to check if image is valid house/garage exterior
      const reader = new FileReader()
      reader.onload = (e) => {
        setHouseImage(e.target.result)
      }
      reader.readAsDataURL(file)
    }
  }

  const handleReset = () => {
    setHouseImage(null)
    setImageFile(null)
    setAnalysisResults(null)
    setSelectedItems([])
    setSelectedProducts({})
    setApiError(null)
    setEditedImage(null)
    setViewMode('original')
  }

  const handleViewToggle = async () => {
    // STRICT VALIDATION - Before any API call

    // Check 1: Image uploaded
    if (!imageFile) {
      setApiError('⚠️ Please upload an image first.')
      setShowAnalysisModal(false)
      return
    }

    // Check 2: Items selected
    if (selectedItems.length === 0) {
      setApiError('⚠️ Please select at least one item from the sidebar (Roofing, Siding, or Trim).')
      setShowAnalysisModal(false)
      return
    }

    // Check 3: API connected
    if (!apiConnected) {
      setApiError('⚠️ Backend API is not connected. Please start the backend server.')
      setShowAnalysisModal(false)
      return
    }

    // If already in edited view, switch back to original
    if (viewMode === 'edited') {
      setViewMode('original')
      setShowAnalysisModal(false)
      return
    }

    // All validations passed - Clear any previous errors
    setApiError(null)

    // Show modal immediately (will show loading state)
    setShowAnalysisModal(true)

    // Step 1: Analyze image (if not already analyzed)
    let currentAnalysisResults = analysisResults
    if (!currentAnalysisResults) {
      setIsAnalyzing(true)
      setApiError(null)

      try {
        const results = await analyzeExterior(imageFile, selectedProducts)

        // Store results (valid or invalid)
        setAnalysisResults(results)
        currentAnalysisResults = results

        // Check if image validation failed
        if (results.valid_exterior_image === false) {
          setApiError(results.reason || "Please upload a house or garage exterior image")
          setIsAnalyzing(false)
          return // Don't proceed to editing if invalid
        }
      } catch (error) {
        setApiError(`Analysis failed: ${error.message}`)
        setAnalysisResults(null)
        setIsAnalyzing(false)
        return
      } finally {
        setIsAnalyzing(false)
      }
    } else {
      // If already analyzed, just show modal with existing results
      return
    }

    // Step 2: Edit image and show edited view
    setIsEditing(true)
    setApiError(null)

    try {
      const editedImageUrl = await editImage(imageFile, currentAnalysisResults, selectedProducts)
      setEditedImage(editedImageUrl)
      setViewMode('edited')
    } catch (error) {
      setApiError(`Failed to edit image: ${error.message}`)
    } finally {
      setIsEditing(false)
    }
  }

  const handleDownload = async () => {
    // STRICT VALIDATION - Before any API call

    // Check 1: Image uploaded
    if (!imageFile) {
      setApiError('⚠️ Please upload an image first.')
      return
    }

    // Check 2: Items selected
    if (selectedItems.length === 0) {
      setApiError('⚠️ Please select at least one item from the sidebar (Roofing, Siding, or Trim).')
      return
    }

    // Check 3: API connected
    if (!apiConnected) {
      setApiError('⚠️ Backend API is not connected. Please start the backend server.')
      return
    }

    // Clear any previous errors
    setApiError(null)

    // Step 1: Analyze image (if not already analyzed)
    let currentAnalysisResults = analysisResults
    if (!currentAnalysisResults) {
      setIsAnalyzing(true)
      setApiError(null)

      try {
        const results = await analyzeExterior(imageFile, selectedProducts)

        // Check if image validation failed
        if (results.valid_exterior_image === false) {
          setApiError(results.reason || "Please upload a house or garage exterior image")
          setAnalysisResults(results) // Store invalid result
          setIsAnalyzing(false)
          return
        }

        setAnalysisResults(results)
        currentAnalysisResults = results // Use the fresh results
      } catch (error) {
        setApiError(`Analysis failed: ${error.message}`)
        setAnalysisResults(null)
        setIsAnalyzing(false)
        return
      } finally {
        setIsAnalyzing(false)
      }
    }

    // Step 2: Edit image
    setIsEditing(true)
    setApiError(null)

    try {
      // Get edited image (create new if not cached)
      const editedImageUrl = editedImage || await editImage(imageFile, currentAnalysisResults, selectedProducts)

      // Download the image
      const link = document.createElement('a')
      link.href = editedImageUrl
      link.download = 'edited_house_image.jpg'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)

      // Clean up blob URL if we just created it
      if (!editedImage) {
        URL.revokeObjectURL(editedImageUrl)
      }
    } catch (error) {
      setApiError(`Failed to download image: ${error.message}`)
    } finally {
      setIsEditing(false)
    }
  }

  const handleSubItemClick = (product) => {
    console.log('Product clicked:', product.name, 'Category:', activeCategory)

    // Map category to region name
    const categoryToRegion = {
      'Roofing': 'roof',
      'Siding': 'siding',
      'Trim': 'trim',
      'Accessories': null // Accessories don't map to specific regions
    }

    const regionName = categoryToRegion[activeCategory]

    if (regionName) {
      // Check if this exact product is already selected
      const isCurrentlySelected = selectedItems.includes(regionName) &&
        selectedProducts[regionName]?.product_name === product.name

      if (isCurrentlySelected) {
        // DESELECT: Remove from selectedItems and selectedProducts
        setSelectedItems(selectedItems.filter(item => item !== regionName))
        const updatedProducts = { ...selectedProducts }
        delete updatedProducts[regionName]
        setSelectedProducts(updatedProducts)
        console.log('Deselected:', regionName)
      } else {
        // SELECT: Add or update selection
        if (!selectedItems.includes(regionName)) {
          setSelectedItems([...selectedItems, regionName])
          console.log('Added to selected items:', regionName)
        }

        const updatedProducts = {
          ...selectedProducts,
          [regionName]: {
            product_name: product.name,
            color: product.pricing?.[0]?.gauge || 'Standard',
            finish: 'Standard'
          }
        }
        setSelectedProducts(updatedProducts)
        console.log('Updated products:', updatedProducts)
      }

      // Selection changed - analysis will be re-done on next View click
      // NO AUTO-RESET - Keep current view mode and edited image
    } else {
      console.log(`Selected: ${activeCategory} - ${product.name} (no region mapping)`)
    }
  }

  return (
    <div className="visualizer-layout">
      {/* Connection Status Indicator */}
      <ConnectionStatus isConnected={apiConnected} />

      {/* 1. Loading Overlay */}
      {(isAnalyzing || isEditing) && (
        <Loader message={isEditing ? "Applying materials..." : "Analyzing structure..."} />
      )}

      <LeftCategorySidebar
        activeCategory={activeCategory}
        onCategoryChange={handleCategoryChange}
      />

      {/* 2. Products Panel (Conditional) */}
      {activeCategory && productData[activeCategory] && (
        <div className="sub-items-panel">
          <div className="sub-items-header">
            <div className="header-row">
              <h3>{activeCategory}</h3>
              {selectedItems.length > 0 && (
                <div className="selected-items-indicator">
                  {selectedItems.length} item{selectedItems.length > 1 ? 's' : ''} selected
                </div>
              )}
            </div>
          </div>
          <div className="sub-items-content">
            <div className="product-list">
              {productData[activeCategory].map((product, index) => {
                const categoryToRegion = {
                  'Roofing': 'roof',
                  'Siding': 'siding',
                  'Trim': 'trim',
                  'Accessories': null
                }
                const regionName = categoryToRegion[activeCategory]
                const isSelected = regionName && selectedItems.includes(regionName) &&
                  selectedProducts[regionName]?.product_name === product.name

                return (
                  <div
                    key={index}
                    className={`product-card ${isSelected ? 'selected' : ''}`}
                    onClick={(e) => {
                      e.preventDefault()
                      e.stopPropagation()
                      handleSubItemClick(product)
                    }}
                    onMouseDown={(e) => e.preventDefault()}
                  >
                    {/* Updated Card Structure */}
                    <div className="product-image-container">
                      {product.image_url ? (
                        <img
                          src={product.image_url}
                          alt={product.name}
                          className="product-thumb"
                          onError={(e) => {
                            e.target.style.display = 'none';
                            e.target.nextSibling.style.display = 'block';
                          }}
                        />
                      ) : null}
                      {/* Fallback / Placeholder */}
                      <span
                        className="product-placeholder"
                        style={{ display: product.image_url ? 'none' : 'block' }}
                      >
                        {product.image || '🏗️'}
                      </span>

                      {isSelected && (
                        <div className="selected-badge">✓</div>
                      )}
                    </div>

                    <div className="product-info">
                      <h4 className="product-name">{product.name}</h4>
                      {product.coverage && (
                        <div className="product-meta">{product.coverage}</div>
                      )}
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      )}

      <ImageCanvas
        houseImage={viewMode === 'edited' && editedImage ? editedImage : houseImage}
        hasSubPanel={!!activeCategory}
        analysisResults={analysisResults}
        isAnalyzing={isAnalyzing}
        apiError={apiError}
        apiConnected={apiConnected}
        viewMode={viewMode}
        isEditing={isEditing}
        hasSelectedItems={selectedItems.length > 0}
      />


      <AnalysisResultModal
        isOpen={showAnalysisModal}
        onClose={() => setShowAnalysisModal(false)}
        analysisResults={analysisResults}
        isAnalyzing={isAnalyzing}
        apiError={apiError}
      />
      <RightActionSidebar
        onImageUpload={handleImageUpload}
        onReset={handleReset}
        onViewToggle={handleViewToggle}
        onDownload={handleDownload}
        isAnalyzing={isAnalyzing}
        hasAnalysis={!!analysisResults}
        viewMode={viewMode}
        isEditing={isEditing}
        hasImage={!!imageFile}
        hasSelectedItems={selectedItems.length > 0}
        isValidImage={analysisResults && analysisResults.valid_exterior_image === true}
      />
    </div>
  )
}

export default VisualizerLayout

