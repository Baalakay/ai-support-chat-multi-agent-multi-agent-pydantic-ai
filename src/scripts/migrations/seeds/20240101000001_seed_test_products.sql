-- Seed initial test products
-- Migration: 20240101000001_seed_test_products

-- Test product 1: Basic electrical component
insert into products (
    model_number,
    category,
    specifications,
    features,
    metadata
) values (
    'TEST-E100',
    'electrical',
    '{
        "electrical": {
            "voltage": "24V",
            "current": "10A",
            "power": "240W",
            "frequency": "60Hz"
        },
        "physical": {
            "width": "10cm",
            "height": "5cm",
            "depth": "3cm",
            "weight": "250g"
        }
    }'::jsonb,
    array[
        'Overcurrent protection',
        'LED status indicators',
        'DIN rail mounting',
        'Surge protection'
    ],
    '{
        "series": "E100",
        "certification": ["CE", "UL"],
        "warranty_years": 2
    }'::jsonb
);

-- Test product 2: Advanced mechanical system
insert into products (
    model_number,
    category,
    specifications,
    features,
    metadata
) values (
    'TEST-M200',
    'mechanical',
    '{
        "mechanical": {
            "max_load": "500kg",
            "operating_temp": "-20C to 60C",
            "material": "316 Stainless Steel",
            "protection_class": "IP67"
        },
        "mounting": {
            "bolt_size": "M12",
            "mounting_points": 4,
            "torque_spec": "50Nm"
        }
    }'::jsonb,
    array[
        'Corrosion resistant',
        'High load capacity',
        'Easy installation',
        'Maintenance-free'
    ],
    '{
        "series": "M200",
        "certification": ["ISO9001"],
        "warranty_years": 5
    }'::jsonb
);

-- Test product 3: Software system
insert into products (
    model_number,
    category,
    specifications,
    features,
    metadata
) values (
    'TEST-S300',
    'software',
    '{
        "system": {
            "os_support": ["Windows 10", "Linux"],
            "min_memory": "8GB",
            "storage": "50GB",
            "processor": "x86_64"
        },
        "network": {
            "protocols": ["TCP/IP", "Modbus"],
            "security": "TLS 1.3",
            "bandwidth": "100Mbps"
        }
    }'::jsonb,
    array[
        'Real-time monitoring',
        'Data encryption',
        'Remote access',
        'Automated backup'
    ],
    '{
        "series": "S300",
        "license_type": "perpetual",
        "support_level": "premium"
    }'::jsonb
);

-- Verify data
select model_number, category, jsonb_pretty(specifications) as specs
from products
where model_number like 'TEST-%'; 