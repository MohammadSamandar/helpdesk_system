from django.shortcuts import render,redirect, get_object_or_404
from .models import Ticket, TicketStatus
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import TicketForm, CommentForm # فرمی که ساختیم برای ایجاد تیکت و پاسخ رو وارد میکنیم
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.utils import timezone
from django.http import HttpResponse

# ویو مربوط به صفحه اصلی
@login_required # این دکوراتور تضمین می‌کند که فقط کاربران لاگین‌کرده به این ویو دسترسی دارند
def index(request):
    # ابتدا نقش کاربر را بررسی می‌کنیم
    if request.user.groups.filter(name='Agent').exists():
        # اگر کاربر عضو گروه کارشناسان بود، او را به داشبورد خودش هدایت کن
        return redirect('agent_dashboard')
    


    # اگر کاربر کارشناس نبود (یعنی یک مشتری عادی است)
    # طبق روال قبل، فقط تیکت‌های خودش را به او نشان بده

    tickets = [] # به صورت پیش فرض لیست تیکت ها خالی است

    if request.user.is_authenticated:
        # اگر کاربر لاگین کرده، تیکت‌هایی را فیلتر کن که نویسنده‌شان همین کاربر است
        tickets = Ticket.objects.filter(author=request.user).order_by('-created_at')

    return render(request, 'tickets/index.html', {'tickets':tickets})

# ویو مربوط به صفحه جزییات تیکت
@login_required # مرحله ۱: کاربر حتما باید لاگین کرده باشد
def ticket_by_id(request, ticket_id):

    ticket = get_object_or_404(Ticket, pk=ticket_id)

    # بررسی سطح دسترسی
    is_agent = request.user.groups.filter(name="Agent").exists()
    is_author = (ticket.author == request.user)

    # اگر کاربر نه کارشناس بود و نه نویسنده تیکت، به صفحه اصلی برگردان
    if not (is_agent or is_author):
        return redirect('index')

    # پردازش فرم ارسال پاسخ یا کامنت
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.ticket = ticket
            comment.author = request.user
            comment.save()

            # تغییر وضعیت تیکت
            is_agent = request.user.groups.filter(name='Agent').exists()
            if is_agent:
                # اگر کارشناس پاسخ داد، وضعیت به "در انتظار پاسخ مشتری" تغییر می‌کند
                ticket.status = TicketStatus.awaiting_customer_response
            else:
                # اگر مشتری پاسخ داد، وضعیت به "در حال بررسی" تغییر می‌کند
                ticket.status = TicketStatus.in_Rreview
                # زمان آخرین فعالیت تیکت را هم بخ روز میکنیم
                ticket.last_activity = timezone.now()
            ticket.save()

            return redirect('ticket_by_id', ticket_id = ticket.id)
    else:
        form = CommentForm()


    comments = ticket.comments.all()
     # بخش جدید: افزودن منطق به ویو برای بررسی نقش نویسنده هر کامنت
    for comment in comments:
        # حالا هر آبجکت کامنت، یک خصوصیت جدید به نام is_from_agent دارد
        comment.is_from_agent = comment.author.groups.filter(name='Agent').exists()

    context = {
        'comments': comments,
        'ticket':ticket,
        'form':form,
        'is_agent': is_agent, 

    }

    
    # اگر دسترسی مجاز بود، صفحه جزئیات را نمایش بده
    return render(request, 'tickets/ticket_by_id.html', context)


# ویو ثبت نام کاربر
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid:
            user = form.save() # کاربر جدید در دیتابیس ذخیره میشود
            login(request, user) # کاربر بلافاصله بعد از ثبت نام لاگین میشه
            return redirect('index') # کاربر به صفحه اصلی هدایت میشود
    else:
        form = UserCreationForm()

    return render(request, 'registration/signup.html', {'form':form})
    



@login_required # این دکوراتور دسترسی به این ویو را فقط برای کاربران لاگین‌کرده مجاز می‌کند
def create_ticket(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False) # تیکت را در حافظه بساز اما در دیتابیس ذخیره نکن
            ticket.author = request.user # نویسنده تیکت را کاربر فعلی قرار بده
            ticket.save() # حالا تیکت را با نویسنده مشخص شده، ذخیره کن
            return redirect('index') # به صفحه اصلی برگرد
    else:
        form = TicketForm()
    return render(request, 'tickets/create_ticket.html', {'form': form})
        



@login_required
def agent_dashboard(request):
    # چک کردن دسترسی کارشناس
    if not request.user.groups.filter(name='Agent').exists():
        # اگر کاربر عضو گروه کارشناسان نبود به صفحه اصلی برگردان
        return redirect('index')
    # تیکت های تخصیص نیافته
    unassigned_ticket = Ticket.objects.filter(assignee__isnull=True).order_by('-created_at')

    #  تیکت‌هایی که فقط به کارشناس فعلی اختصاص یافته‌اند
    my_assigned_tickets  = Ticket.objects.filter(assignee=request.user).order_by('-updated_at')


    # بقیه تیکت‌ها (تخصیص یافته به دیگر کارشناسان)
    # ما با exclude، تیکت‌های خودمان را از این لیست حذف می‌کنیم

    other_tickets = Ticket.objects.filter(assignee__isnull=False).order_by('-created_at').exclude(assignee=request.user)

    context = {
        'unassigned_tickets': unassigned_ticket,
        'my_assigned_tickets': my_assigned_tickets, 
        'all_tickets': other_tickets,
    }

    return render(request, 'tickets/agent_dashboard.html', context)




# برای دکمه یا امکان اختصاص دادن تیکت به خود برای کارشناس
@login_required
def assigne_ticket(request,ticket_id):
    # دسترسی فقط برای کارشناس مجاز است
    if not request.user.groups.filter(name='Agent').exists():
        return redirect('index')
    
    # پیدا کردن تیکت مورد نظر
    ticket = get_object_or_404(Ticket, id=ticket_id)

    # ثبت کارشناس فعلی به عنوان مسئول یا پاسخ دهنده تیکت
    ticket.assignee = request.user
    ticket.status = TicketStatus.in_Rreview
    ticket.save()

    return redirect('agent_dashboard')


# با این کلاس ویو لاگین پیش فرض جنگو رو کمی تغییر میدیم و میگیم که
#  هر کاربر بعد از لاگین با توجه به نقشش به کجا هدایت بشه
class CustomLoginView(LoginView):
    # ما همچنان از همان تمپلیت لاگین قبلی استفاده میکنیم
    template_name = 'registration/login.html'

    def get_success_url(self):
        """
        این متد پس از ورود موفق کاربر اجرا می‌شود و تصمیم می‌گیرد
        کاربر به کدام آدرس هدایت شود.
        """
        user = self.request.user

        # چک می‌کنیم آیا کاربر عضو گروه "Agents" است یا خیر
        if user.groups.filter(name='Agent').exists():
        # اگر کارشناس بود، به داشبورد کارشناسان هدایت شود
            return reverse_lazy('agent_dashboard')
        
        else:
            # در غیر این صورت (کاربر عادی)، به صفحه اصلی هدایت شود
            return reverse_lazy('index')
        








@login_required
def close_ticket(request, ticket_id):
    # این خط باید دقیقاً با نام گروهی که در ادمین ساختید، یکی باشد
    if not request.user.groups.filter(name='Agent').exists():
        return redirect('index')
    
    ticket = get_object_or_404(Ticket, id=ticket_id)
    ticket.status = TicketStatus.closed
    ticket.save()
    return redirect('ticket_by_id', ticket_id=ticket.id)
    

# ticketApp/views.py

@login_required
def reopen_ticket(request, ticket_id):
    if not request.user.groups.filter(name='Agent').exists():
        return redirect('index')
    ticket = get_object_or_404(Ticket, id=ticket_id)


    #  آخرین کامنت را پیدا می‌کنیم
    last_comment = ticket.comments.last()

    if last_comment:
        # اگر کامنتی وجود داشت، نویسنده آن را بررسی می‌کنیم
        is_last_commenter_agent = last_comment.author.groups.filter(name='Agent').exists()

        if is_last_commenter_agent:
            # اگر آخرین نفر کارشناس بوده، پس حالا نوبت مشتری است
            ticket.status = TicketStatus.awaiting_customer_response
        else:
            # اگر آخرین نفر مشتری بوده، پس حالا نوبت کارشناس است
            ticket.status = TicketStatus.in_Rreview
    else:
        #  اگر هیچ کامنتی وجود نداشت، تیکت به حالت بررسی اولیه برمی‌گردد
        ticket.status = TicketStatus.in_Rreview

    # در هر صورت، تیکت را ذخیره کرده و به صفحه جزئیات برمی‌گردیم
    ticket.save()
    return redirect('ticket_by_id', ticket_id=ticket.id)



