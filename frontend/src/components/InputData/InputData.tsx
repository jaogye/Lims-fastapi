import { useState, useRef } from 'react';
import { AgGridReact } from 'ag-grid-react';
import { ColDef } from 'ag-grid-community';
import { apiService } from '../../services/api';
import type { SampleDetailResponse, QualityInfoItem, CreateSampleResponse } from '../../types';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';
import * as XLSX from 'xlsx';

function InputData() {
  const today = new Date().toISOString().split('T')[0];

  // State
  const [selectedDate, setSelectedDate] = useState<string>(today);
  const [samples, setSamples] = useState<SampleDetailResponse[]>([]);
  const [selectedSample, setSelectedSample] = useState<SampleDetailResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [successMessage, setSuccessMessage] = useState<string>('');

  // Error console state
  const [showErrorConsole, setShowErrorConsole] = useState(false);
  const [errorMessages, setErrorMessages] = useState<string>('');
  const [pendingData, setPendingData] = useState<any[]>([]);

  // Tank dropdown options
  const [tankOptions, setTankOptions] = useState<{ id: number; name: string }[]>([]);

  const qualityGridRef = useRef<AgGridReact>(null);

  // Check if sample is complete (all measurements have values)
  const isSampleComplete = (sample: SampleDetailResponse): boolean => {
    return sample.quality_info.every(item => item.value !== null && item.value !== undefined);
  };

  // Get sample color based on completion status
  const getSampleColor = (sample: SampleDetailResponse): string => {
    return isSampleComplete(sample) ? '#4caf50' : '#ff9800';
  };

  // Handle Get Data button click
  const handleGetData = async () => {
    if (!selectedDate) {
      setError('Please select a date');
      return;
    }

    setLoading(true);
    setError('');
    setSuccessMessage('');
    setShowErrorConsole(false);

    try {
      // Step 1: Create samples
      const createResponse: CreateSampleResponse = await apiService.createSamples(selectedDate);

      // Check for errors in customer_result or production_result
      const hasCustomerErrors = createResponse.customer_result.errors && createResponse.customer_result.errors.length > 0;
      const hasProductionErrors = createResponse.production_result.errors && createResponse.production_result.errors.length > 0;

      if (hasCustomerErrors || hasProductionErrors) {
        const allErrors: string[] = [];

        if (hasCustomerErrors) {
          allErrors.push('Customer Errors:');
          allErrors.push(...(createResponse.customer_result.errors || []));
        }

        if (hasProductionErrors) {
          allErrors.push('Production Errors:');
          allErrors.push(...(createResponse.production_result.errors || []));
        }

        setErrorMessages(allErrors.join('\n'));

        // Show pending data if available
        if (createResponse.customer_result.pending_data && createResponse.customer_result.pending_data.length > 0) {
          setPendingData(createResponse.customer_result.pending_data);
        }

        setShowErrorConsole(true);
      }

      // Step 2: Get samples
      const samplesData = await apiService.getSamples(selectedDate);
      setSamples(samplesData);
      setSelectedSample(null);

      setSuccessMessage(`Loaded ${samplesData.length} samples for ${selectedDate}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load samples');
      setSamples([]);
    } finally {
      setLoading(false);
    }
  };

  // Handle sample selection
  const handleSampleClick = async (sample: SampleDetailResponse) => {
    setSelectedSample(sample);

    // Load tank options for this sample
    if (sample.sample_product_id && sample.sample_quality_id) {
      try {
        const tanks = await apiService.getSamplePointsByProductQuality(
          sample.sample_product_id,
          sample.sample_quality_id
        );
        setTankOptions(tanks);
      } catch (err: any) {
        console.error('Failed to load tank options:', err);
        setTankOptions([]);
      }
    } else {
      setTankOptions([]);
    }
  };

  // Handle measurement value change
  const handleValueChange = (variable: string, newValue: string) => {
    if (!selectedSample) return;

    const updatedQualityInfo = selectedSample.quality_info.map(item =>
      item.variable === variable
        ? { ...item, value: newValue ? parseFloat(newValue) : undefined }
        : item
    );

    const updatedSample = {
      ...selectedSample,
      quality_info: updatedQualityInfo
    };

    setSelectedSample(updatedSample);

    // Update in samples array
    setSamples(samples.map(s =>
      s.sample_number === selectedSample.sample_number ? updatedSample : s
    ));
  };

  // Handle field changes (container, tank, batch, remark)
  const handleFieldChange = (field: string, value: string) => {
    if (!selectedSample) return;

    const updatedSample = {
      ...selectedSample,
      [field]: value || undefined
    };

    setSelectedSample(updatedSample);

    // Update in samples array
    setSamples(samples.map(s =>
      s.sample_number === selectedSample.sample_number ? updatedSample : s
    ));
  };

  // Handle Update button
  const handleUpdate = async () => {
    if (samples.length === 0) {
      setError('No samples to update');
      return;
    }

    setLoading(true);
    setError('');
    setSuccessMessage('');

    try {
      await apiService.updateSamples(samples);
      setSuccessMessage('Samples updated successfully');

      // Reload samples to get updated data
      const samplesData = await apiService.getSamples(selectedDate);
      setSamples(samplesData);

      // Update selected sample if it exists
      if (selectedSample) {
        const updated = samplesData.find(s => s.sample_number === selectedSample.sample_number);
        if (updated) {
          setSelectedSample(updated);
        }
      }
    } catch (err: any) {
      // Handle structured error response from validation
      const errorDetail = err.response?.data?.detail;
      if (errorDetail && typeof errorDetail === 'object') {
        // If detail is an object with message and errors
        const errorMsg = errorDetail.message || 'Failed to update samples';
        const errorList = errorDetail.errors || [];

        if (errorList.length > 0) {
          setError(`${errorMsg}\n\n${errorList.join('\n')}`);
        } else {
          setError(errorMsg);
        }
      } else {
        // If detail is a simple string
        setError(errorDetail || 'Failed to update samples');
      }
    } finally {
      setLoading(false);
    }
  };

  // Handle report generation
  const handleGenerateReport = async (reportType: 'coa' | 'coc' | 'day-certificate') => {
    if (!selectedSample) return;

    setLoading(true);
    setError('');

    try {
      let blob: Blob;

      switch (reportType) {
        case 'coa':
          blob = await apiService.generateCOA(selectedSample.sample_number);
          break;
        case 'coc':
          blob = await apiService.generateCOC(selectedSample.sample_number);
          break;
        case 'day-certificate':
          blob = await apiService.generateDayCertificate(selectedSample.sample_number);
          break;
      }

      // Download the PDF
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${reportType}_${selectedSample.sample_number}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      setSuccessMessage(`${reportType.toUpperCase()} generated successfully`);
    } catch (err: any) {
      setError(err.response?.data?.detail || `Failed to generate ${reportType}`);
    } finally {
      setLoading(false);
    }
  };

  // Download error messages
  const handleDownloadMessages = () => {
    const blob = new Blob([errorMessages], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `sample_errors_${selectedDate}.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  };

  // Download pending data as Excel
  const handleDownloadPendings = () => {
    if (pendingData.length === 0) return;

    const ws = XLSX.utils.json_to_sheet(pendingData);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Pending Data');
    XLSX.writeFile(wb, `pending_data_${selectedDate}.xlsx`);
  };

  // Quality info grid columns
  const qualityColumnDefs: ColDef<QualityInfoItem>[] = [
    { field: 'variable', headerName: 'Variable', flex: 1, sortable: true },
    { field: 'min', headerName: 'Min', width: 100, sortable: true },
    { field: 'max', headerName: 'Max', width: 100, sortable: true },
    {
      field: 'value',
      headerName: 'Value',
      width: 120,
      editable: true,
      cellStyle: { backgroundColor: '#fff9e6' }
    }
  ];

  // Pending data grid columns (dynamic based on data)
  const getPendingDataColumns = (): ColDef[] => {
    if (pendingData.length === 0) return [];

    const firstRow = pendingData[0];
    return Object.keys(firstRow).map(key => ({
      field: key,
      headerName: key,
      sortable: true,
      filter: true,
      resizable: true
    }));
  };

  return (
    <div>
      <div className="page-header">
        <h1>Input Data</h1>
        <p>Input measurement results for laboratory samples</p>
      </div>

      {error && <div className="error-message" style={{ whiteSpace: 'pre-line' }}>{error}</div>}
      {successMessage && <div className="success-message">{successMessage}</div>}

      {/* Date Selection and Get Data */}
      <div style={{
        display: 'flex',
        gap: '15px',
        alignItems: 'flex-end',
        marginBottom: '20px',
        padding: '15px',
        border: '1px solid #ddd',
        borderRadius: '8px',
        backgroundColor: '#f9f9f9'
      }}>
        <div className="form-group" style={{ marginBottom: 0, flex: '0 0 200px' }}>
          <label htmlFor="sample-date">Sample Date *</label>
          <input
            id="sample-date"
            type="date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            disabled={loading}
          />
        </div>

        <button
          className="btn btn-primary"
          onClick={handleGetData}
          disabled={loading}
        >
          {loading ? 'Loading...' : 'Get Data'}
        </button>

        <button
          className="btn btn-primary"
          onClick={handleUpdate}
          disabled={loading || samples.length === 0}
          style={{ marginLeft: 'auto' }}
        >
          Update
        </button>
      </div>

      {/* Error Console */}
      {showErrorConsole && (
        <div style={{
          border: '2px solid #d32f2f',
          borderRadius: '8px',
          padding: '15px',
          marginBottom: '20px',
          backgroundColor: '#ffebee'
        }}>
          <h3 style={{ marginTop: 0, color: '#d32f2f' }}>Errors During Sample Loading</h3>

          <div style={{ marginBottom: '15px' }}>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
              Error Messages:
            </label>
            <textarea
              value={errorMessages}
              readOnly
              style={{
                width: '100%',
                minHeight: '100px',
                fontFamily: 'monospace',
                fontSize: '12px',
                padding: '8px',
                border: '1px solid #ccc',
                borderRadius: '4px'
              }}
            />
            <button
              className="btn btn-secondary"
              onClick={handleDownloadMessages}
              style={{ marginTop: '8px' }}
            >
              Download Messages (txt)
            </button>
          </div>

          {pendingData.length > 0 && (
            <div>
              <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                Pending Data ({pendingData.length} rows):
              </label>
              <div className="ag-theme-alpine" style={{ height: '200px', width: '100%', marginBottom: '10px' }}>
                <AgGridReact
                  rowData={pendingData}
                  columnDefs={getPendingDataColumns()}
                  defaultColDef={{
                    sortable: true,
                    filter: true,
                    resizable: true
                  }}
                />
              </div>
              <button
                className="btn btn-secondary"
                onClick={handleDownloadPendings}
              >
                Download Pendings (Excel)
              </button>
            </div>
          )}
        </div>
      )}

      {/* Main Layout */}
      <div style={{ display: 'grid', gridTemplateColumns: '250px 1fr', gap: '20px' }}>
        {/* Sample List */}
        <div style={{
          border: '1px solid #ddd',
          borderRadius: '8px',
          padding: '10px',
          backgroundColor: '#f9f9f9',
          maxHeight: '600px',
          overflowY: 'auto'
        }}>
          <h3 style={{ marginTop: 0, marginBottom: '15px', fontSize: '16px' }}>
            Samples ({samples.length})
          </h3>

          {samples.length === 0 ? (
            <p style={{ color: '#666', fontSize: '14px' }}>No samples loaded</p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
              {samples.map((sample) => (
                <button
                  key={sample.sample_number}
                  onClick={() => handleSampleClick(sample)}
                  style={{
                    padding: '10px',
                    border: selectedSample?.sample_number === sample.sample_number
                      ? '2px solid #1976d2'
                      : '1px solid #ccc',
                    borderRadius: '4px',
                    backgroundColor: getSampleColor(sample),
                    color: 'white',
                    cursor: 'pointer',
                    textAlign: 'left',
                    fontWeight: selectedSample?.sample_number === sample.sample_number ? 'bold' : 'normal',
                    fontSize: '13px'
                  }}
                >
                  {sample.sample_number}
                  <div style={{ fontSize: '11px', marginTop: '2px', opacity: 0.9 }}>
                    {sample.product}
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Sample Details */}
        <div>
          {selectedSample ? (
            <>
              {/* Sample Information */}
              <div style={{
                border: '1px solid #ddd',
                borderRadius: '8px',
                padding: '15px',
                marginBottom: '20px',
                backgroundColor: '#f9f9f9'
              }}>
                <h3 style={{ marginTop: 0, marginBottom: '15px' }}>
                  Sample: {selectedSample.sample_number}
                </h3>

                {/* Read-only fields */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '10px', fontSize: '14px', marginBottom: '15px' }}>
                  <div><strong>Customer:</strong> {selectedSample.customer_name || 'N/A'}</div>
                  <div><strong>Product:</strong> {selectedSample.product}</div>
                  <div><strong>Quality:</strong> {selectedSample.quality}</div>
                  <div><strong>Date:</strong> {selectedSample.sample_date}</div>
                  <div><strong>Order INC:</strong> {selectedSample.orderPVS || 'N/A'}</div>
                  <div><strong>Order Client:</strong> {selectedSample.orderclient || 'N/A'}</div>
                </div>

                {/* Editable fields */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '15px' }}>
                  <div className="form-group" style={{ marginBottom: 0 }}>
                    <label htmlFor="tank">Tank</label>
                    <select
                      id="tank"
                      value={selectedSample.tank || ''}
                      onChange={(e) => handleFieldChange('tank', e.target.value)}
                      disabled={loading}
                    >
                      <option value="">-- Select Tank --</option>
                      {tankOptions.map((tank) => (
                        <option key={tank.id} value={tank.name}>
                          {tank.name}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="form-group" style={{ marginBottom: 0 }}>
                    <label htmlFor="container">Container</label>
                    <input
                      id="container"
                      type="text"
                      value={selectedSample.container_number || ''}
                      onChange={(e) => handleFieldChange('container_number', e.target.value)}
                      disabled={loading}
                      placeholder="Container number"
                    />
                  </div>

                  <div className="form-group" style={{ marginBottom: 0 }}>
                    <label htmlFor="batch">Batch</label>
                    <input
                      id="batch"
                      type="text"
                      value={selectedSample.batch_number || ''}
                      onChange={(e) => handleFieldChange('batch_number', e.target.value)}
                      disabled={loading}
                      placeholder="Batch number"
                    />
                  </div>

                  <div className="form-group" style={{ marginBottom: 0 }}>
                    <label htmlFor="remark">Remark</label>
                    <input
                      id="remark"
                      type="text"
                      value={selectedSample.remark || ''}
                      onChange={(e) => handleFieldChange('remark', e.target.value)}
                      disabled={loading}
                      placeholder="Remark"
                    />
                  </div>
                </div>

                {/* Report Buttons */}
                <div style={{ display: 'flex', gap: '10px', marginTop: '15px' }}>
                  {selectedSample.sample_coa === 'Y' && (
                    <button
                      className="btn btn-secondary"
                      onClick={() => handleGenerateReport('coa')}
                      disabled={loading}
                    >
                      COA
                    </button>
                  )}

                  {selectedSample.sample_coc === 'Y' && (
                    <button
                      className="btn btn-secondary"
                      onClick={() => handleGenerateReport('coc')}
                      disabled={loading}
                    >
                      COC
                    </button>
                  )}

                  {selectedSample.sample_day_coa === 'Y' && (
                    <button
                      className="btn btn-secondary"
                      onClick={() => handleGenerateReport('day-certificate')}
                      disabled={loading}
                    >
                      C of day
                    </button>
                  )}
                </div>
              </div>

              {/* Quality Info Grid */}
              <div style={{
                border: '1px solid #ddd',
                borderRadius: '8px',
                padding: '15px',
                backgroundColor: '#f9f9f9'
              }}>
                <h3 style={{ marginTop: 0, marginBottom: '15px' }}>
                  Measurements
                </h3>

                <div className="ag-theme-alpine" style={{ height: '400px', width: '100%' }}>
                  <AgGridReact
                    ref={qualityGridRef}
                    rowData={selectedSample.quality_info}
                    columnDefs={qualityColumnDefs}
                    defaultColDef={{
                      sortable: true,
                      filter: false,
                      resizable: true
                    }}
                    onCellValueChanged={(params) => {
                      handleValueChange(params.data.variable, params.newValue);
                    }}
                    singleClickEdit={true}
                  />
                </div>
              </div>
            </>
          ) : (
            <div style={{
              border: '1px solid #ddd',
              borderRadius: '8px',
              padding: '40px',
              textAlign: 'center',
              color: '#666',
              backgroundColor: '#f9f9f9'
            }}>
              <p>Select a sample from the list to view and edit measurements</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default InputData;
