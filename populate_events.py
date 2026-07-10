import os
import django
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EventDiscoveryPlatform.settings')
django.setup()

from accounts.models import User
from events.models import Event, EventCategory


def run():
    print("Starting data seeding script...")

    # 1. Create or get likith003
    user, created = User.objects.get_or_create(username='likith003')
    user.email = 'likith003@example.com'
    user.role = 'organizer'
    user.is_approved = True
    user.full_name = 'Likith Reddy'
    user.mobile_number = '+91-9876543210'
    if created or not user.check_password('likith123'):
        user.set_password('likith123')
    user.save()
    print(f"Organizer User: likith003 ({'Created new' if created else 'Existing updated'}) — Password: 'likith123'")

    # Clean previous test events to prevent duplicates
    Event.objects.filter(organizer=user).delete()
    print("Cleaned up old events by likith003.")

    now = timezone.now()

    events_data = [
        # ─── CSE → GMOCS ──────────────────────────────────────────────────────
        {
            'event_name': 'GMOCS 2026 — CSE National Tech Symposium',
            'description': (
                'One Day National Technical Symposium hosted by the Department of Computer Science & Engineering.\n\n'
                'Events include:\n'
                '• Code Debugging Championship\n'
                '• Paper Presentations on AI, ML & Cloud\n'
                '• Technical Web Design Wars\n'
                '• Project Poster Exhibition\n\n'
                'Registration fee includes food coupons, entry kit and certificate.'
            ),
            'category': EventCategory.EDUCATION,
            'date': now + timedelta(days=15, hours=2),
            'venue': 'CSE Seminar Hall, Block A',
            'ticket_price': Decimal('150.00'),
            'ticket_price_vip': Decimal('350.00'),
            'ticket_price_premium': Decimal('500.00'),
            'capacity': 200,
            'department': 'Computer Science & Engineering (CSE)',
            'agenda': (
                '09:00 AM — Inauguration Ceremony\n'
                '10:00 AM — Paper Presentation Finals\n'
                '01:00 PM — Lunch Break\n'
                '02:00 PM — Coding Championship & Debugging\n'
                '04:00 PM — Valedictory & Prize Distribution'
            ),
            'contact_email': 'cse.gmocs@example.com',
            'contact_phone': '+91-9876543210'
        },
        # ─── CSE-Cyber → EPICS ────────────────────────────────────────────────
        {
            'event_name': 'EPICS — Cyber Security Fest 2026',
            'description': (
                'National level cyber symposium featuring hands-on war games and ethical hacking workshops.\n\n'
                'Events include:\n'
                '• Capture The Flag (CTF) — Jeopardy Style\n'
                '• Lock-Picking Challenge\n'
                '• Wireshark Traffic Analysis Test\n'
                '• Social Engineering Awareness Workshop\n\n'
                'Organized by the CSE-Cyber Security department. All skill levels welcome.'
            ),
            'category': EventCategory.EDUCATION,
            'date': now + timedelta(days=18, hours=3),
            'venue': 'Main Auditorium, Block C',
            'ticket_price': Decimal('200.00'),
            'ticket_price_vip': Decimal('450.00'),
            'ticket_price_premium': Decimal('700.00'),
            'capacity': 150,
            'department': 'CSE — Cyber Security',
            'agenda': (
                '09:30 AM — Opening Keynote: Zero Trust Architecture\n'
                '10:30 AM — CTF Competition Launch\n'
                '01:30 PM — Networking Lunch\n'
                '02:30 PM — Threat Hunting Workshops\n'
                '04:30 PM — Winner Announcements & Felicitation'
            ),
            'contact_email': 'cyber.epics@example.com',
            'contact_phone': '+91-8765432109'
        },
        # ─── National Technical Symposium ─────────────────────────────────────
        {
            'event_name': 'One Day National Technical Symposium 2026',
            'description': (
                'A grand inter-collegiate engineering symposium hosting student designs and product presentations '
                'across all core branches — Mechanical, ECE, Civil, CSE, and IT.\n\n'
                'Free entry for all registered students with valid college ID. '
                'Industry judges, funded internship opportunities and awards worth ₹50,000 up for grabs!'
            ),
            'category': EventCategory.EDUCATION,
            'date': now + timedelta(days=25, hours=1),
            'venue': 'Sardar Patel Convocation Center',
            'ticket_price': Decimal('0.00'),
            'ticket_price_vip': Decimal('0.00'),
            'ticket_price_premium': Decimal('0.00'),
            'capacity': 500,
            'department': 'Engineering & Technology Council',
            'agenda': (
                '09:00 AM — Chief Guest Welcome Speech\n'
                '10:00 AM — Project Expo (All Blocks)\n'
                '12:30 PM — Panel Discussion: Industry 4.0\n'
                '02:00 PM — CAD Design & Robo Race Wars\n'
                '04:30 PM — Awards Ceremony & Closure'
            ),
            'contact_email': 'techsymp2026@example.com',
            'contact_phone': '+91-7654321098'
        },
        # ─── Music ────────────────────────────────────────────────────────────
        {
            'event_name': 'Rooftop Acoustic Music Jam Night',
            'description': (
                'Enjoy an evening under the stars listening to acoustic strings, soft jazz, '
                'and open mic performances by local student bands.\n\n'
                'VIP pass includes front-row cushion seating and mocktail voucher.\n'
                'Premium pass includes artist meet & greet and exclusive merchandise.'
            ),
            'category': EventCategory.MUSIC,
            'date': now + timedelta(days=5, hours=6),
            'venue': 'Block D Terrace Lounge',
            'ticket_price': Decimal('100.00'),
            'ticket_price_vip': Decimal('250.00'),
            'ticket_price_premium': Decimal('400.00'),
            'capacity': 80,
            'department': 'Fine Arts Club',
            'agenda': (
                '06:00 PM — Gate opening & Welcome Mocktails\n'
                '06:30 PM — Student Bands Openers\n'
                '08:00 PM — Headliner Solo Acoustic Sets\n'
                '09:30 PM — Open Mic Session'
            ),
            'contact_email': 'music.arts@example.com',
            'contact_phone': '+91-6543210987'
        },
        # ─── Business ─────────────────────────────────────────────────────────
        {
            'event_name': 'Startup Founders Round-Table 2026',
            'description': (
                'Hear from alumni founders about securing pre-seed funding, pivoting models during search phase, '
                'and building initial marketing momentum.\n\n'
                'VIP attendees will get a 15-minute private mentoring slot with one founder. '
                'Premium includes a signed copy of "Zero to One" and curated resources bundle.'
            ),
            'category': EventCategory.BUSINESS,
            'date': now + timedelta(days=12, hours=4),
            'venue': 'Campus Incubation Center, Room 102',
            'ticket_price': Decimal('200.00'),
            'ticket_price_vip': Decimal('500.00'),
            'ticket_price_premium': Decimal('800.00'),
            'capacity': 60,
            'department': 'E-Cell & Entrepreneurship',
            'agenda': (
                '02:00 PM — Founders Introductions\n'
                '02:30 PM — Modulated Q&A Panel\n'
                '03:30 PM — Networking Coffee Session\n'
                '04:30 PM — VIP Mentoring Slots (VIP & Premium Only)'
            ),
            'contact_email': 'ecell@example.com',
            'contact_phone': '+91-5432109876'
        },
        # ─── Food ─────────────────────────────────────────────────────────────
        {
            'event_name': 'Gourmet Street Food Carnival',
            'description': (
                'Taste dynamic recipes, artisanal chocolates, organic beverages, and fusion food stalls '
                'prepared by student culinary artists.\n\n'
                'Entry is FREE! VIP wristband gives unlimited tasting at premium stalls. '
                'Premium pass includes a guided chef tour and cooking masterclass access.'
            ),
            'category': EventCategory.FOOD,
            'date': now + timedelta(days=8, hours=5),
            'venue': 'Campus Quadrangle Garden',
            'ticket_price': Decimal('0.00'),
            'ticket_price_vip': Decimal('150.00'),
            'ticket_price_premium': Decimal('300.00'),
            'capacity': 400,
            'department': 'Hotel & Catering Management',
            'agenda': (
                '11:00 AM — Food Stalls Open\n'
                '02:00 PM — MasterChef Student Challenge\n'
                '04:00 PM — Chef Masterclass (Premium)\n'
                '05:00 PM — Live Music & Bakery Reviews'
            ),
            'contact_email': 'catering.culinary@example.com',
            'contact_phone': '+91-4321098765'
        },
        # ─── Sports ───────────────────────────────────────────────────────────
        {
            'event_name': 'Inter-Departmental Athletics Meet 2026',
            'description': (
                'Annual campus sports championship covering track and field events, short sprints, relays, '
                'and long jumps across all departments.\n\n'
                'Entry is FREE for all students. VIP stand tickets give covered seating access. '
                'Premium includes a sports kit bag & goodies.'
            ),
            'category': EventCategory.SPORTS,
            'date': now + timedelta(days=22, hours=2),
            'venue': 'Netaji Stadium Track',
            'ticket_price': Decimal('0.00'),
            'ticket_price_vip': Decimal('100.00'),
            'ticket_price_premium': Decimal('200.00'),
            'capacity': 300,
            'department': 'Physical Education Department',
            'agenda': (
                '08:00 AM — 100m Sprints Heats\n'
                '09:30 AM — Long Jump Finals\n'
                '11:00 AM — 4×100m Mixed Relay Finals\n'
                '01:00 PM — Closing Ceremony & Trophy Presentation'
            ),
            'contact_email': 'sports.pe@example.com',
            'contact_phone': '+91-3210987654'
        },
        # ─── Arts ─────────────────────────────────────────────────────────────
        {
            'event_name': 'Spectrum — Annual Cultural Arts Fest',
            'description': (
                'A multi-day cultural extravaganza celebrating dance, drama, fashion, and visual arts. '
                'Experience breathtaking solo and group dance battles, theatrical plays, '
                'fashion walks designed by fashion design students, and live mural painting.\n\n'
                'Premium pass holders get exclusive backstage access.'
            ),
            'category': EventCategory.CULTURAL,
            'date': now + timedelta(days=30, hours=3),
            'venue': 'Open Air Amphitheatre',
            'ticket_price': Decimal('75.00'),
            'ticket_price_vip': Decimal('200.00'),
            'ticket_price_premium': Decimal('400.00'),
            'capacity': 600,
            'department': 'Fine Arts & Cultural Studies',
            'agenda': (
                '04:00 PM — Gates Open & Welcome Installation Art\n'
                '05:00 PM — Dance Battle Round 1\n'
                '06:30 PM — Fashion Walk\n'
                '07:30 PM — Theatrical Play\n'
                '09:00 PM — Headliner Dance Showcase & Closure'
            ),
            'contact_email': 'spectrum.arts@example.com',
            'contact_phone': '+91-2109876543'
        },
    ]

    for val in events_data:
        event = Event.objects.create(
            organizer=user,
            event_name=val['event_name'],
            description=val['description'],
            category=val['category'],
            date=val['date'],
            venue=val['venue'],
            ticket_price=val['ticket_price'],
            ticket_price_vip=val['ticket_price_vip'],
            ticket_price_premium=val['ticket_price_premium'],
            capacity=val['capacity'],
            department=val['department'],
            agenda=val['agenda'],
            contact_email=val['contact_email'],
            contact_phone=val['contact_phone'],
        )
        print(f"  [OK] Created: '{event.event_name}'  (Rs.{event.ticket_price} / Rs.{event.ticket_price_vip} / Rs.{event.ticket_price_premium})")

    print("\nData seeding completed successfully!")


if __name__ == '__main__':
    run()
