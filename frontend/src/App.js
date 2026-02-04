import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Container, Navbar, Tab, Tabs, Table, Button, Form, Row, Col, Card, Alert, Badge, Modal, InputGroup } from 'react-bootstrap';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Leaflet 아이콘 설정
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

// 지도 중심 변경 컴포넌트
function ChangeView({ center, zoom }) {
  const map = useMap();
  map.setView(center, zoom);
  return null;
}

function App() {
  // 탭 상태
  const [key, setKey] = useState('dashboard');
  
  // 데이터 상태
  const [vessels, setVessels] = useState([]);
  const [seafarers, setSeafarers] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [noonReports, setNoonReports] = useState([]);
  const [certs, setCerts] = useState([]);
  const [workHours, setWorkHours] = useState([]);

  // 필터링 및 지도 상태
  const [filterVesselId, setFilterVesselId] = useState(null);
  const [mapCenter, setMapCenter] = useState([20, 120]);
  const [mapZoom, setMapZoom] = useState(2);

  // 정렬 및 검색 상태
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'ascending' });
  const [searchTerm, setSearchTerm] = useState('');

  // 모달 상태
  const [showVesselModal, setShowVesselModal] = useState(false);
  const [showCrewModal, setShowCrewModal] = useState(false);
  
  // 폼 데이터 상태
  const [vesselForm, setVesselForm] = useState({ name: '', imo_number: '', vessel_type: 'CONTAINER', built_year: 2020 });
  const [seafarerForm, setSeafarerForm] = useState({ name: '', rank: 'ABLE_SEAMAN', nationality: 'Korea', vessel: '' });

  // 데이터 로드
  const fetchAll = async () => {
    try {
      const endpoints = ['vessels', 'seafarers', 'maintenance-jobs', 'noon-reports', 'certificates', 'work-hours'];
      const responses = await Promise.all(endpoints.map(ep => axios.get(`http://15.164.251.186:8000/api/${ep}/`)));
      
      setVessels(responses[0].data);
      setSeafarers(responses[1].data);
      setJobs(responses[2].data);
      setNoonReports(responses[3].data);
      setCerts(responses[4].data);
      setWorkHours(responses[5].data);
    } catch (e) { console.error("데이터 로딩 실패:", e); }
  };

  useEffect(() => { fetchAll(); }, []);

  // 탭 변경 시 초기화
  const handleTabSelect = (k) => {
    setKey(k);
    setSortConfig({ key: null, direction: 'ascending' });
    setSearchTerm('');
    if (k !== 'seafarers') setFilterVesselId(null);
  };

  // --- [LOGIC] 정렬 및 검색 ---
  const requestSort = (key) => {
    let direction = 'ascending';
    if (sortConfig.key === key && sortConfig.direction === 'ascending') {
      direction = 'descending';
    }
    setSortConfig({ key, direction });
  };

  const getProcessedData = (data) => {
    let filteredData = data;
    if (searchTerm) {
      filteredData = data.filter(item => 
        Object.values(item).some(val => 
          val && val.toString().toLowerCase().includes(searchTerm.toLowerCase())
        )
      );
    }
    if (key === 'seafarers' && filterVesselId) {
      filteredData = filteredData.filter(s => s.vessel === filterVesselId);
    }
    if (sortConfig.key) {
      filteredData.sort((a, b) => {
        let valA = a[sortConfig.key] ? a[sortConfig.key].toString().toLowerCase() : '';
        let valB = b[sortConfig.key] ? b[sortConfig.key].toString().toLowerCase() : '';
        if (!isNaN(a[sortConfig.key]) && !isNaN(b[sortConfig.key])) {
            valA = Number(a[sortConfig.key]);
            valB = Number(b[sortConfig.key]);
        }
        if (valA < valB) return sortConfig.direction === 'ascending' ? -1 : 1;
        if (valA > valB) return sortConfig.direction === 'ascending' ? 1 : -1;
        return 0;
      });
    }
    return filteredData;
  };

  const renderSortIcon = (colKey) => {
    if (sortConfig.key !== colKey) return <span style={{color:'#ccc'}}> ↕</span>;
    return sortConfig.direction === 'ascending' ? ' ▲' : ' ▼';
  };

  const SortableHeader = ({ label, colKey }) => (
    <th 
      style={{ cursor: 'pointer', userSelect: 'none', backgroundColor: sortConfig.key === colKey ? '#e9ecef' : 'inherit' }} 
      onClick={() => requestSort(colKey)}
    >
      {label} {renderSortIcon(colKey)}
    </th>
  );

  // --- [HANDLERS] ---
  const handleGoToMap = (vesselName) => {
    const target = vessels.find(v => v.name === vesselName);
    if (target && target.latitude) {
      setMapCenter([target.latitude, target.longitude]);
      setMapZoom(6);
      handleTabSelect('dashboard');
    } else { alert("선박 정보를 찾을 수 없습니다."); }
  };

  const handleGoToCrewList = (vesselId) => {
    setFilterVesselId(vesselId);
    handleTabSelect('seafarers');
  };

  const handleVesselSubmit = () => { axios.post('http://15.164.251.186:8000/api/vessels/', vesselForm).then(() => { alert("등록 완료"); setShowVesselModal(false); fetchAll(); }); };
  const handleCrewSubmit = () => { axios.post('http://15.164.251.186:8000/api/seafarers/', seafarerForm).then(() => { alert("승선 완료"); setShowCrewModal(false); fetchAll(); }); };
  const handleNoonReportSubmit = (e) => { e.preventDefault(); const formData = new FormData(e.target); const data = Object.fromEntries(formData.entries()); axios.post('http://15.164.251.186:8000/api/noon-reports/', data).then(() => { alert("전송 완료"); fetchAll(); }); };
  const handleCompleteJob = (job) => { if (window.confirm("완료 처리하시겠습니까?")) { const today = new Date().toISOString().split('T')[0]; axios.patch(`http://15.164.251.186:8000/api/maintenance-jobs/${job.id}/`, { last_performed: today }).then(() => { alert("완료되었습니다."); fetchAll(); }); }};

  return (
    <div className="App">
      <Navbar bg="dark" variant="dark" expand="lg" className="mb-4">
        <Container>
          <Navbar.Brand>Smart VMS (통합 관리)</Navbar.Brand>
        </Container>
      </Navbar>

      <Container>
        <div className="d-flex flex-column flex-md-row justify-content-between mb-3 gap-2">
            {key !== 'dashboard' && key !== 'cii' && (
               <InputGroup style={{ maxWidth: '300px' }}>
                 <InputGroup.Text>🔍</InputGroup.Text>
                 <Form.Control placeholder="검색어 입력..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} />
               </InputGroup>
            )}
            <div className="d-flex gap-2 justify-content-end">
                {filterVesselId && key === 'seafarers' && (
                    <Button variant="secondary" size="sm" onClick={() => setFilterVesselId(null)}>필터 해제</Button>
                )}
                <Button variant="outline-primary" size="sm" onClick={() => setShowVesselModal(true)}>+ 선박 등록</Button>
                <Button variant="outline-success" size="sm" onClick={() => setShowCrewModal(true)}>+ 선원 승선</Button>
            </div>
        </div>

        {certs.filter(c => c.days_left <= 30).length > 0 && (
          <Alert variant="danger">
            <strong>[경고]</strong> 30일 이내 만료 예정인 증서가 {certs.filter(c => c.days_left <= 30).length}건 있습니다. (증서 관리 탭 확인)
          </Alert>
        )}

        <Tabs activeKey={key} onSelect={handleTabSelect} className="mb-3" style={{overflowX: 'auto', flexWrap: 'nowrap'}}>
          
          {/* 1. 관제 대시보드 */}
          <Tab eventKey="dashboard" title="관제 대시보드">
            <Row>
              <Col lg={8} xs={12} className="mb-3">
                <div style={{ height: '500px', border: '1px solid #ddd', borderRadius:'8px', overflow:'hidden' }}>
                  <MapContainer center={mapCenter} zoom={mapZoom} style={{ height: '100%', width: '100%' }}>
                    <ChangeView center={mapCenter} zoom={mapZoom} />
                    <TileLayer attribution='&copy; OpenStreetMap' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
                    {vessels.map(v => (
                       v.latitude && (
                        <Marker key={v.id} position={[v.latitude, v.longitude]}>
                            <Popup>
                                <strong>{v.name}</strong><br/>
                                <Button size="sm" variant="link" onClick={() => handleGoToCrewList(v.id)}>승선원 확인</Button>
                            </Popup>
                        </Marker>
                       )
                    ))}
                  </MapContainer>
                </div>
              </Col>
              
              {/* ▼▼▼ 운항 일보 입력 폼 (예시 추가됨) ▼▼▼ */}
              <Col lg={4} xs={12}>
                <Card>
                    <Card.Header>운항 일보 입력 (Noon Report)</Card.Header>
                    <Card.Body>
                    <Form onSubmit={handleNoonReportSubmit}>
                        <Form.Group className="mb-2">
                        <Form.Select name="vessel" required>
                            <option value="">선박을 선택하세요</option>
                            {vessels.map(v => <option key={v.id} value={v.id}>{v.name}</option>)}
                        </Form.Select>
                        </Form.Group>
                        <Row>
                            <Col><Form.Control name="latitude" placeholder="위도 (예: 35.10)" required /></Col>
                            <Col><Form.Control name="longitude" placeholder="경도 (예: 129.04)" required /></Col>
                        </Row>
                        <Form.Control className="mt-2" name="distance" placeholder="운항 거리 (예: 340 NM)" required />
                        <Form.Control className="mt-2" name="fuel_consumption" placeholder="연료 소모 (예: 42.5 MT)" required />
                        <Form.Control className="mt-2" name="sog" placeholder="평균 속도 (예: 14.5 Kts)" required />
                        <Form.Control type="date" name="report_date" defaultValue={new Date().toISOString().split('T')[0]} className="mt-2" />
                        <Button type="submit" variant="dark" className="w-100 mt-3">전송 (위치 업데이트)</Button>
                    </Form>
                    </Card.Body>
                </Card>
              </Col>
            </Row>
          </Tab>

          {/* 2. 선박 목록 */}
          <Tab eventKey="vessels" title={`선박 목록 (${getProcessedData(vessels).length})`}>
            <div className="table-responsive">
              <Table striped bordered hover>
                <thead className="table-light">
                  <tr>
                    <SortableHeader label="선박명" colKey="name" />
                    <SortableHeader label="IMO" colKey="imo_number" />
                    <SortableHeader label="선종" colKey="type_display" />
                    <SortableHeader label="건조년도" colKey="built_year" />
                    <th>승선원 (Link)</th>
                    <th>위치 (Link)</th>
                  </tr>
                </thead>
                <tbody>
                  {getProcessedData(vessels).map(v => (
                    <tr key={v.id}>
                      <td>{v.name}</td>
                      <td>{v.imo_number}</td>
                      <td><Badge bg="info">{v.type_display}</Badge></td>
                      <td>{v.built_year}</td>
                      <td><Button variant="link" size="sm" onClick={() => handleGoToCrewList(v.id)}>{v.crew_count} 명 ➡️</Button></td>
                      <td><Button variant="outline-dark" size="sm" onClick={() => handleGoToMap(v.name)}>지도 🌏</Button></td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            </div>
          </Tab>

          {/* 3. 승선원 명부 */}
          <Tab eventKey="seafarers" title={`승선원 명부 (${getProcessedData(seafarers).length})`}>
             {filterVesselId && <Alert variant="info" className="p-2">선택한 선박의 선원만 표시 중입니다.</Alert>}
             <div className="table-responsive">
              <Table striped bordered hover>
                <thead className="table-light">
                  <tr>
                    <SortableHeader label="성명" colKey="name" />
                    <SortableHeader label="직책" colKey="rank_display" />
                    <SortableHeader label="국적" colKey="nationality" />
                    <SortableHeader label="승선 선박" colKey="vessel_name" />
                  </tr>
                </thead>
                <tbody>
                  {getProcessedData(seafarers).map(s => (
                    <tr key={s.id}>
                      <td>{s.name}</td>
                      <td>{s.rank_display}</td>
                      <td>{s.nationality}</td>
                      <td>{s.vessel_name ? <span style={{color:'blue', cursor:'pointer', textDecoration:'underline'}} onClick={() => handleGoToMap(s.vessel_name)}>{s.vessel_name}</span> : <span className="text-muted">대기 중</span>}</td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            </div>
          </Tab>

          {/* 4. PMS 정비 */}
          <Tab eventKey="pms" title="PMS 정비">
            <div className="table-responsive">
              <Table bordered hover>
                <thead className="table-light">
                  <tr>
                    <SortableHeader label="상태" colKey="is_overdue" />
                    <SortableHeader label="선박" colKey="vessel_name" />
                    <SortableHeader label="작업명" colKey="job_title" />
                    <SortableHeader label="최근 정비" colKey="last_performed" />
                    <SortableHeader label="다음 예정" colKey="next_due_date" />
                    <th>작업</th>
                  </tr>
                </thead>
                <tbody>
                  {getProcessedData(jobs).map(job => (
                    <tr key={job.id} className={job.is_overdue ? "table-danger" : ""}>
                      <td>{job.is_overdue ? <Badge bg="danger">Overdue</Badge> : <Badge bg="success">Normal</Badge>}</td>
                      <td><span style={{color:'blue', cursor:'pointer'}} onClick={() => handleGoToMap(job.vessel_name)}>{job.vessel_name}</span></td>
                      <td>{job.job_title}</td>
                      <td>{job.last_performed}</td>
                      <td style={{fontWeight: job.is_overdue?'bold':'normal'}}>{job.next_due_date}</td>
                      <td><Button size="sm" onClick={() => handleCompleteJob(job)}>완료</Button></td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            </div>
          </Tab>

          {/* 5. CII 모니터링 */}
          <Tab eventKey="cii" title="CII 모니터링">
             <div style={{ height: 400 }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={noonReports}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="report_date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="fuel_consumption" stroke="#8884d8" name="연료 소모량" />
                </LineChart>
              </ResponsiveContainer>
             </div>
          </Tab>
          
           {/* 6. 근로 관리 */}
           <Tab eventKey="workrest" title="근로 관리">
             <div className="table-responsive">
               <Table bordered hover>
                 <thead className="table-light">
                    <tr>
                        <SortableHeader label="선원명" colKey="seafarer_name" />
                        <SortableHeader label="날짜" colKey="date" />
                        <SortableHeader label="근무시간" colKey="work_hours" />
                        <SortableHeader label="상태" colKey="is_violation" />
                    </tr>
                 </thead>
                 <tbody>
                   {getProcessedData(workHours).map(w => (
                     <tr key={w.id} className={w.is_violation ? "table-danger" : ""}>
                       <td>{w.seafarer_name}</td>
                       <td>{w.date}</td>
                       <td>{w.work_hours}H</td>
                       <td>{w.is_violation ? <Badge bg="danger">위반</Badge> : <Badge bg="success">정상</Badge>}</td>
                     </tr>
                   ))}
                 </tbody>
               </Table>
             </div>
          </Tab>

           {/* 7. 증서 관리 */}
           <Tab eventKey="certs" title="증서 관리">
            <div className="table-responsive">
              <Table striped bordered hover>
                <thead className="table-light">
                    <tr>
                        <SortableHeader label="선박명" colKey="vessel_name" />
                        <SortableHeader label="증서명" colKey="name" />
                        <SortableHeader label="만료일" colKey="expiry_date" />
                        <SortableHeader label="잔여일수" colKey="days_left" />
                    </tr>
                </thead>
                <tbody>
                  {getProcessedData(certs).map(c => (
                    <tr key={c.id}>
                      <td>{c.vessel_name}</td>
                      <td>{c.name}</td>
                      <td>{c.expiry_date}</td>
                      <td>{c.days_left <= 30 ? <Badge bg="danger">{c.days_left}일 (임박)</Badge> : <span>{c.days_left}일</span>}</td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            </div>
          </Tab>

        </Tabs>
        
        {/* 모달 */}
        <Modal show={showVesselModal} onHide={() => setShowVesselModal(false)}>
          <Modal.Header closeButton><Modal.Title>신규 선박 등록</Modal.Title></Modal.Header>
          <Modal.Body>
            <Form>
              <Form.Group className="mb-3"><Form.Label>선박명</Form.Label><Form.Control type="text" placeholder="예: HMM Algeciras" onChange={(e) => setVesselForm({...vesselForm, name: e.target.value})} /></Form.Group>
              <Form.Group className="mb-3"><Form.Label>IMO 번호</Form.Label><Form.Control type="text" placeholder="예: 9863297" onChange={(e) => setVesselForm({...vesselForm, imo_number: e.target.value})} /></Form.Group>
              <Form.Group className="mb-3"><Form.Label>선종</Form.Label><Form.Select onChange={(e) => setVesselForm({...vesselForm, vessel_type: e.target.value})}><option value="CONTAINER">컨테이너</option><option value="BULK">벌크</option><option value="LNG">LNG</option><option value="TANKER">유조선</option></Form.Select></Form.Group>
              <Form.Group className="mb-3"><Form.Label>건조년도</Form.Label><Form.Control type="number" defaultValue={2020} onChange={(e) => setVesselForm({...vesselForm, built_year: e.target.value})} /></Form.Group>
            </Form>
          </Modal.Body>
          <Modal.Footer><Button variant="secondary" onClick={() => setShowVesselModal(false)}>취소</Button><Button variant="primary" onClick={handleVesselSubmit}>등록</Button></Modal.Footer>
        </Modal>

        <Modal show={showCrewModal} onHide={() => setShowCrewModal(false)}>
          <Modal.Header closeButton><Modal.Title>선원 승선 처리</Modal.Title></Modal.Header>
          <Modal.Body>
            <Form>
              <Form.Group className="mb-3"><Form.Label>성명</Form.Label><Form.Control type="text" placeholder="예: 홍길동" onChange={(e) => setSeafarerForm({...seafarerForm, name: e.target.value})} /></Form.Group>
              <Form.Group className="mb-3"><Form.Label>직책</Form.Label><Form.Select onChange={(e) => setSeafarerForm({...seafarerForm, rank: e.target.value})}><option value="ABLE_SEAMAN">갑판수</option><option value="CAPTAIN">선장</option><option value="CHIEF_MATE">1항사</option><option value="CHIEF_ENGINEER">기관장</option></Form.Select></Form.Group>
              <Form.Group className="mb-3"><Form.Label>국적</Form.Label><Form.Control type="text" defaultValue="Korea" onChange={(e) => setSeafarerForm({...seafarerForm, nationality: e.target.value})} /></Form.Group>
              <Form.Group className="mb-3"><Form.Label>선박</Form.Label><Form.Select onChange={(e) => setSeafarerForm({...seafarerForm, vessel: e.target.value})}><option value="">선박 선택...</option>{vessels.map(v => <option key={v.id} value={v.id}>{v.name}</option>)}</Form.Select></Form.Group>
            </Form>
          </Modal.Body>
          <Modal.Footer><Button variant="secondary" onClick={() => setShowCrewModal(false)}>취소</Button><Button variant="success" onClick={handleCrewSubmit}>승선</Button></Modal.Footer>
        </Modal>

      </Container>
    </div>
  );
}

export default App;