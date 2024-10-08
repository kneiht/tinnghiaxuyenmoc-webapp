from django.template.loader import render_to_string
from django.urls import reverse


def html_render( component, request, **kwargs):
    if component=='card':
        context = {
                'record': kwargs.get('record'), 
                'card': kwargs.get('card'),
        }
        template = 'components/card.html'

    elif component=='message':
        context = {
                'modal': 'modal_message',
                'message': kwargs.get('message'),
                'message_type': kwargs.get('message_type'),
                'message_title': kwargs.get('message_title'),
        }
        template = 'components/modal.html'

    elif component=='form':      
        context = {
                'form': kwargs.get('form'), 
                'modal': kwargs.get('modal'),
                'record': kwargs.get('record'),
        } 
        modal = kwargs.get('modal')
        record = kwargs.get('record')
        if not record:
            context['submit_button_name'] = 'Tạo mới'
            if modal == 'modal_project':
                context['title'] = 'Tạo dự án mới'
                context['form_url'] = reverse('api_projects')
            elif modal == 'modal_job':
                context['title'] = 'Tạo công việc mới'
                context['form_url'] = reverse('api_jobs')
        else: 
            context['submit_button_name'] = 'Cập nhật'
            if modal == 'modal_project':
                context['title'] = 'Cập nhật dự án'
                context['form_url'] = reverse('api_project_pk', kwargs={'pk': record.pk})
            elif modal == 'modal_job':
                context['title'] = 'Cập nhật công việc'
                context['form_url'] = reverse('api_job_pk', kwargs={'pk': record.pk})

        template = 'components/modal.html'


    elif component=='display_cards':
        context = {
                'records': kwargs.get('records'),
        }
        template = 'components/display_cards.html'

    return render_to_string(template, context, request)