export const CHANDIGARH_SECTOR17_PARCELS: any = {
  type: 'FeatureCollection',
  features: [
    {
      type: 'Feature',
      id: 'P-101',
      properties: {
        parcel_id: 'P-101',
        status: 'validated',
        confidence: 97,
        area: 850,
        land_use: 'Commercial',
        owner: 'Municipal Corp.',
        spatial_score: 98,
        attribute_score: 96,
        source_agreement: 100,
        recommendation: 'All 5 sources in strong geometric and attribute agreement. Fully reconciled.',
        sources: { cadastral: true, revenue: true, municipal: true, gnss: true, drone: true },
        source_records: [
          { source_type: 'Cadastral Map', is_valid: 'valid' },
          { source_type: 'Revenue Record', is_valid: 'valid' },
          { source_type: 'Municipal GIS', is_valid: 'valid' },
          { source_type: 'GNSS Survey', is_valid: 'valid' },
          { source_type: 'Drone Survey', is_valid: 'valid' },
        ]
      },
      geometry: {
        type: 'Polygon',
        coordinates: [[[76.7760, 30.7440], [76.7775, 30.7440], [76.7775, 30.7430], [76.7760, 30.7430], [76.7760, 30.7440]]]
      }
    },
    {
      type: 'Feature',
      id: 'P-102',
      properties: {
        parcel_id: 'P-102',
        status: 'validated',
        confidence: 95,
        area: 1200,
        land_use: 'Commercial',
        owner: 'State Govt.',
        spatial_score: 96,
        attribute_score: 94,
        source_agreement: 95,
        recommendation: 'Good alignment across sources. Validated.',
        sources: { cadastral: true, revenue: true, municipal: true, gnss: true, drone: true },
        source_records: [
          { source_type: 'Cadastral Map', is_valid: 'valid' },
          { source_type: 'Revenue Record', is_valid: 'valid' },
          { source_type: 'Municipal GIS', is_valid: 'valid' },
        ]
      },
      geometry: {
        type: 'Polygon',
        coordinates: [[[76.7780, 30.7440], [76.7798, 30.7440], [76.7798, 30.7430], [76.7780, 30.7430], [76.7780, 30.7440]]]
      }
    },
    {
      type: 'Feature',
      id: 'P-103',
      properties: {
        parcel_id: 'P-103',
        status: 'review',
        confidence: 74,
        area: 960,
        land_use: 'Mixed Use',
        owner: 'Private',
        spatial_score: 78,
        attribute_score: 72,
        source_agreement: 70,
        recommendation: 'Boundary discrepancy between revenue map and drone imagery. Human inspection required.',
        sources: { cadastral: true, revenue: true, municipal: true, gnss: false, drone: true },
        source_records: [
          { source_type: 'Cadastral Map', is_valid: 'valid' },
          { source_type: 'Revenue Record', is_valid: 'valid' },
        ]
      },
      geometry: {
        type: 'Polygon',
        coordinates: [[[76.7802, 30.7440], [76.7818, 30.7440], [76.7818, 30.7430], [76.7802, 30.7430], [76.7802, 30.7440]]]
      }
    },
    {
      type: 'Feature',
      id: 'P-104',
      properties: {
        parcel_id: 'P-104',
        status: 'conflict',
        confidence: 58,
        area: 1000,
        land_use: 'Residential',
        owner: 'Private',
        spatial_score: 62,
        attribute_score: 55,
        source_agreement: 50,
        recommendation: 'Area mismatch detected: Cadastral reports 1,000 m², drone survey reveals 1,035 m² (+3.5%). Resurvey recommended.',
        sources: { cadastral: true, revenue: true, municipal: true, gnss: true, drone: true },
        source_records: [
          { source_type: 'Cadastral Map', is_valid: 'valid' },
          { source_type: 'Drone Survey', is_valid: 'warning' },
        ]
      },
      geometry: {
        type: 'Polygon',
        coordinates: [[[76.7760, 30.7425], [76.7780, 30.7425], [76.7780, 30.7415], [76.7760, 30.7415], [76.7760, 30.7425]]]
      }
    },
    {
      type: 'Feature',
      id: 'P-107',
      properties: {
        parcel_id: 'P-107',
        status: 'conflict',
        confidence: 45,
        area: 1400,
        land_use: 'Institutional',
        owner: 'State Govt.',
        spatial_score: 52,
        attribute_score: 40,
        source_agreement: 40,
        recommendation: 'Missing record from Revenue department. Available sources show 8.6% area variance.',
        sources: { cadastral: true, revenue: false, municipal: true, gnss: true, drone: true },
        source_records: [
          { source_type: 'Cadastral Map', is_valid: 'valid' },
          { source_type: 'Municipal GIS', is_valid: 'valid' },
        ]
      },
      geometry: {
        type: 'Polygon',
        coordinates: [[[76.7760, 30.7413], [76.7782, 30.7413], [76.7782, 30.7403], [76.7760, 30.7403], [76.7760, 30.7413]]]
      }
    },
    {
      type: 'Feature',
      id: 'P-110',
      properties: {
        parcel_id: 'P-110',
        status: 'changed',
        confidence: 88,
        area: 650,
        land_use: 'Commercial',
        owner: 'Municipal Corp.',
        spatial_score: 90,
        attribute_score: 86,
        source_agreement: 85,
        recommendation: 'Temporal change detected: Vacant land converted to commercial complex in 2024.',
        sources: { cadastral: true, revenue: true, municipal: true, gnss: true, drone: true },
        source_records: [
          { source_type: 'Cadastral Map', is_valid: 'valid' },
          { source_type: 'Drone Survey', is_valid: 'valid' },
        ]
      },
      geometry: {
        type: 'Polygon',
        coordinates: [[[76.7768, 30.7400], [76.7782, 30.7400], [76.7782, 30.7392], [76.7768, 30.7392], [76.7768, 30.7400]]]
      }
    },
    {
      type: 'Feature',
      id: 'P-112',
      properties: {
        parcel_id: 'P-112',
        status: 'conflict',
        confidence: 52,
        area: 1300,
        land_use: 'Residential',
        owner: 'Private',
        spatial_score: 55,
        attribute_score: 48,
        source_agreement: 50,
        recommendation: 'Parcel boundaries do not align across sources. 8.5% range in measured area.',
        sources: { cadastral: true, revenue: true, municipal: true, gnss: true, drone: true },
        source_records: [
          { source_type: 'Cadastral Map', is_valid: 'valid' },
          { source_type: 'Revenue Record', is_valid: 'warning' },
        ]
      },
      geometry: {
        type: 'Polygon',
        coordinates: [[[76.7804, 30.7400], [76.7822, 30.7400], [76.7822, 30.7392], [76.7804, 30.7392], [76.7804, 30.7400]]]
      }
    },
    {
      type: 'Feature',
      id: 'P-119',
      properties: {
        parcel_id: 'P-119',
        status: 'conflict',
        confidence: 50,
        area: 1150,
        land_use: 'Commercial',
        owner: 'Disputed',
        spatial_score: 58,
        attribute_score: 42,
        source_agreement: 40,
        recommendation: 'Owner marked "Disputed" in revenue records. Duplicate parcel IDs in municipal records.',
        sources: { cadastral: true, revenue: true, municipal: true, gnss: true, drone: true },
        source_records: [
          { source_type: 'Cadastral Map', is_valid: 'valid' },
          { source_type: 'Revenue Record', is_valid: 'warning' },
        ]
      },
      geometry: {
        type: 'Polygon',
        coordinates: [[[76.7802, 30.7448], [76.7820, 30.7448], [76.7820, 30.7442], [76.7802, 30.7442], [76.7802, 30.7448]]]
      }
    },
    {
      type: 'Feature',
      id: 'P-124',
      properties: {
        parcel_id: 'P-124',
        status: 'conflict',
        confidence: 47,
        area: 820,
        land_use: 'Residential',
        owner: 'Private',
        spatial_score: 54,
        attribute_score: 40,
        source_agreement: 38,
        recommendation: 'Encroachment: Building footprint extends 50 m² beyond recorded boundary. Site inspection required.',
        sources: { cadastral: true, revenue: true, municipal: true, gnss: true, drone: true },
        source_records: [
          { source_type: 'Cadastral Map', is_valid: 'valid' },
          { source_type: 'Drone Survey', is_valid: 'warning' },
        ]
      },
      geometry: {
        type: 'Polygon',
        coordinates: [[[76.7775, 30.7368], [76.7790, 30.7368], [76.7790, 30.7360], [76.7775, 30.7360], [76.7775, 30.7368]]]
      }
    },
  ]
};

export const CHANDIGARH_BUILDINGS: any = {
  type: 'FeatureCollection',
  features: [
    {
      type: 'Feature',
      properties: { building_id: 'BLD-101', floors: 3 },
      geometry: {
        type: 'Polygon',
        coordinates: [[[76.7762, 30.7438], [76.7773, 30.7438], [76.7773, 30.7432], [76.7762, 30.7432], [76.7762, 30.7438]]]
      }
    },
    {
      type: 'Feature',
      properties: { building_id: 'BLD-102', floors: 4 },
      geometry: {
        type: 'Polygon',
        coordinates: [[[76.7782, 30.7438], [76.7796, 30.7438], [76.7796, 30.7432], [76.7782, 30.7432], [76.7782, 30.7438]]]
      }
    },
    {
      type: 'Feature',
      properties: { building_id: 'BLD-124-ENCROACH', floors: 2 },
      geometry: {
        type: 'Polygon',
        coordinates: [[[76.7778, 30.7370], [76.7793, 30.7370], [76.7793, 30.7363], [76.7778, 30.7363], [76.7778, 30.7370]]]
      }
    }
  ]
};
