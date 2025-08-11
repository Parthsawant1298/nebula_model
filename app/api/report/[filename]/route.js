import { NextResponse } from "next/server"

export async function GET(request, { params }) {
  try {
    const { filename } = params
    
    if (!filename) {
      return NextResponse.json({ error: "Filename is required" }, { status: 400 })
    }

    // Forward the report generation request to the Flask backend
    const controller = new AbortController()
    const signal = controller.signal
    
    // Set timeout to 5 minutes for report generation
    const timeout = setTimeout(() => controller.abort(), 5 * 60 * 1000)
    
    const flaskResponse = await fetch(`http://localhost:5000/api/report/${filename}`, {
      signal
    })
    
    clearTimeout(timeout)

    if (!flaskResponse.ok) {
      console.error(`Report generation error: ${flaskResponse.status} ${flaskResponse.statusText}`)
      return NextResponse.json({ 
        error: `Report generation failed: ${flaskResponse.statusText}` 
      }, { status: flaskResponse.status })
    }

    // Get the file data as ArrayBuffer
    const fileData = await flaskResponse.arrayBuffer()
    
    if (!fileData || fileData.byteLength === 0) {
      return NextResponse.json({ error: "Empty report file received from server" }, { status: 500 })
    }

    // Create a response with the file data
    const response = new NextResponse(fileData)

    // Set the content type and disposition headers for PDF
    response.headers.set("Content-Type", "application/pdf")
    response.headers.set("Content-Disposition", `attachment; filename="ML_Project_Report.pdf"`)
    response.headers.set("Content-Length", fileData.byteLength.toString())

    return response
  } catch (error) {
    console.error("Error in report API route:", error)
    return NextResponse.json({ 
      error: error.message || "An error occurred during report generation" 
    }, { status: 500 })
  }
}
